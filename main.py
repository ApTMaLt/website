from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from data import db_session, posts_api
from data.login import LoginForm
from data.users import User
from data.posts import Posts
from forms.user import RegisterForm
from forms.profil import ProfilForm
from forms.search import SearchForm
from forms.post import PostForm
import os
from flask import Flask, flash, request, redirect, jsonify, render_template, make_response, session, abort, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import requests

UPLOAD_FOLDER = 'static/img/original/'
ALLOWED_EXTENSIONS = {'dng', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def scale_image(input_image_path, output_image_path, width=None, height=None):  # изменнеие размеров фотографии
    original_image = Image.open(input_image_path)
    w, h = original_image.size
    if width and height:
        max_size = (width, height)
    elif width:
        max_size = (width, h)
    elif height:
        max_size = (w, height)
    else:
        # No width or height specified
        raise RuntimeError('Width or height required!')
    original_image.thumbnail(max_size, Image.ANTIALIAS)
    original_image.save(output_image_path)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def index():  # главная страница
    searchform = SearchForm()  # форма для поиска
    if searchform.validate_on_submit():
        search = searchform.search.data
    else:
        search = ''
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).filter(Posts.tegs.like(f'%{search}%'))  # поиск изображения с тегом
    response = []
    for i in posts:
        response.append(i)
    response.sort(key=lambda x: x.id, reverse=True)  # сортировка по времени добавления
    return render_template("index.html", posts=response, searchform=searchform, title='Главная страница')


@app.route("/unsplash", methods=['GET', 'POST'])
def unsplash():  # изображения с Unsplash
    searchform = SearchForm()  # форма для поиска
    if searchform.validate_on_submit():
        search = searchform.search.data
    else:
        search = ''
    if search != '':
        unsplash_request = [
            f"https://api.unsplash.com/search/photos?client_id=NGbcLeb-P3bs4CN6I9nxdkQw36zNSnCNz7tF-zGOIws&query={search}"
            f"&per_page=30"]  # поиск 30 изображений с тегом
    else:
        unsplash_request = [
            "https://api.unsplash.com/photos/random?client_id=NGbcLeb-P3bs4CN6I9nxdkQw36zNSnCNz7tF-zGOIws&count=30"]
        # 30 случайных изображений
    for i in unsplash_request:
        response = requests.get(i)  # делаем запрос
        if response:
            json_response = response.json()
            # Преобразуем ответ в json-объект
            if search != '':
                json_response = json_response['results']
        else:
            print(response)
    return render_template("unsplash.html", posts=json_response, searchform=searchform, title='Фото с Unsplash.com')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():  # страница регистрации
    form = RegisterForm()  # форма для регистрации
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:  # проверка на совпадение введённых паролей
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():  # проверка на уникальность email
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if db_sess.query(User).filter(User.username == form.username.data).first():  # проверка на уникальность никнейма
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой никнейм занят")
        # создание новго пользователя
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            username=form.username.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profil', methods=['GET', 'POST'])
def profil():  # страница личного профиля пользователя
    form = ProfilForm()  # форма для личного профиля пользователя
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()  # находим пользователя в базе данных
        if user:
            # автоматически заполняем форму
            form.name.data = user.name
            form.surname.data = user.surname
            form.username.data = user.username
            form.about.data = user.about
            posts = db_sess.query(Posts).filter(Posts.user_uploud == current_user.id)
            response = []
            for i in posts:
                response.append(i)
            response.sort(key=lambda x: x.id, reverse=True)  # сортировка по времени добавления
        else:
            abort(404)
    if form.validate_on_submit():
        # если нажата кнопка сохранить
        db_sess = db_session.create_session()
        # проверка на уникальность никнейма
        if db_sess.query(User).filter(User.username == form.username.data).first() and \
                current_user.id != db_sess.query(User).filter(User.username == form.username.data).first().id:
            return render_template('profil.html', title='Мой профиль',
                                   form=form,
                                   message="Такой никнейм занят")
        # сохраняем изменения
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.name = form.name.data
        user.surname = form.surname.data
        user.username = form.username.data
        user.about = form.about.data
        db_sess.commit()
        return redirect('/')
    return render_template('profil.html', title='Мой профиль', form=form, posts=response)


@app.route('/profil/<int:id>', methods=['GET', 'POST'])
def other_profil(id):  # страница профиля другого пользователя
    form = ProfilForm()  # форма для профиля другого пользователя
    if request.method == "GET":
        if current_user.is_active:
            if id == current_user.id:  # проверка на попытки пользователя открыть свой же профиль
                return redirect('/profil')
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user:
            # заполнение неизменяемых форм
            form.name.data = user.name
            form.surname.data = user.surname
            form.username.data = user.username
            form.about.data = user.about
            posts = db_sess.query(Posts).filter(Posts.user_uploud == id)
            response = []
            for i in posts:
                response.append(i)
            response.sort(key=lambda x: x.id, reverse=True)  # сортировка по времени добавления
        else:
            abort(404)
    return render_template('other_profil.html', user=user, posts=response, title='Профиль ' + str(user.username))


@app.route('/login', methods=['GET', 'POST'])
def login():  # страница для входа
    form = LoginForm()  # форма для входа
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()  # поиск пользователя по email
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)  # если email и пароль верны то происходит вход
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/post', methods=['GET', 'POST'])
@login_required
def add_posts():  # страница для создания поста
    form = PostForm()  # форма для создания поста
    db_sess = db_session.create_session()
    posts = Posts()
    if request.method == 'POST':
        # скачивание изображения
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return render_template('post.html',
                                   message="Файл не выбран",
                                   form=form)
        if file and allowed_file(file.filename):
            # если файл получен и все поля заполнены сохраняем введённое
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            scale_image(input_image_path='static/img/original/' + str(filename),
                        output_image_path='static/img/scaled/' + str(filename),
                        width=800)
            posts.original_f_s_l = 'static/img/original/' + str(filename)
            posts.scaled_f_s_l = 'static/img/scaled/' + str(filename)
            posts.tegs = form.tegs.data
            posts.about = form.about.data
            current_user.posts.append(posts)
            db_sess.merge(current_user)
            db_sess.commit()
            post = db_sess.query(Posts).filter(Posts.tegs == form.tegs.data, Posts.about == form.about.data,
                                               Posts.original_f_s_l == 'static/img/original/' + str(filename),
                                               Posts.scaled_f_s_l == 'static/img/scaled/' + str(filename),
                                               ).first()
            post.original_img = 'http://127.0.0.1:5000/download/' + str(post.id)
            post.scaled_img = 'http://127.0.0.1:5000/download/scaled/' + str(post.id)
            db_sess.commit()
            return redirect('/')
    return render_template('post.html', title='Создание поста',
                           form=form)


@app.route('/download/<int:id>')
def download_file(id):  # страница где сервер отдаёт оригинальный файл пользователю
    db_sess = db_session.create_session()
    post_download = db_sess.query(Posts).filter(Posts.id == id).first()
    return send_file(post_download.original_f_s_l)


@app.route('/download/scaled/<int:id>')
def download_scaled_file(id):  # страница где сервер отдаёт сжатый файл пользователю
    db_sess = db_session.create_session()
    post_download = db_sess.query(Posts).filter(Posts.id == id).first()
    return send_file(post_download.scaled_f_s_l)


@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_posts(id):  # страница для изменения поста
    form = PostForm()  # форма для изменения поста
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id,
                                       (Posts.user == current_user) | (current_user.id == 1)
                                       ).first()
    if request.method == "GET":
        if post:
            # если пост существует то автоматически заполняем поля
            form.tegs.data = post.tegs
            form.about.data = post.about
        else:
            abort(404)
    if request.method == 'POST':
        if post:
            # сохраняем изменения
            post.tegs = form.tegs.data
            post.about = form.about.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('post.html',
                           title='Редактирование поста',
                           form=form,
                           post=post)


@app.route('/post_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def posts_delete(id):  # страница для удаления поста
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).filter(Posts.id == id,
                                        (Posts.user == current_user) | (current_user.id == 1)
                                        ).first()
    if posts:  # существует ли пост
        if os.path.isfile(posts.original_f_s_l):  # существуют ли оригинальное и сжатое изображение
            os.remove(posts.original_f_s_l)
            print("success")
        else:
            print("File doesn't exists!")
        if os.path.isfile(posts.scaled_f_s_l):
            os.remove(posts.scaled_f_s_l)
            print("success")
        else:
            print("File doesn't exists!")
        db_sess.delete(posts)  # удаление поста
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/posts.db")
    app.register_blueprint(posts_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
