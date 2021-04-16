from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from data import db_session
from data.login import LoginForm
from data.users import User
from data.posts import Posts
from forms.user import RegisterForm
from forms.profil import ProfilForm
from forms.post import PostForm
import os
from flask import Flask, flash, request, redirect, url_for, render_template, make_response, session, abort, send_file
from werkzeug.utils import secure_filename
from PIL import Image

UPLOAD_FOLDER = 'static/img/original/'
ALLOWED_EXTENSIONS = {'dng', 'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def scale_image(input_image_path,
                output_image_path,
                width=None,
                height=None
                ):
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


@app.route("/")
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts)
    gg = []
    for i in posts:
        gg.append(i)
    gg.sort(key=lambda x: x.id, reverse=True)
    return render_template("index.html", posts=gg)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой никнейм занят")
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


@app.route('/profil/', methods=['GET', 'POST'])
def profil():
    form = ProfilForm()
    if form.validate_on_submit():
        if not(current_user.check_password(form.old_password.data)):
            return render_template('profil.html', title='Профиль',
                                   form=form,
                                   message="Введён неверный старый пароль")
        if form.password.data != form.password_again.data:
            return render_template('profil.html', title='Регистрация',
                                   form=form,
                                   message="Новые пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == form.username.data).first() and\
                current_user.id != db_sess.query(User).filter(User.username == form.username.data).first().id:
            return render_template('profil.html', title='Регистрация',
                                   form=form,
                                   message="Такой никнейм занят")
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.name = form.name.data
        user.surname = form.surname.data
        user.username = form.username.data
        user.about = form.about.data
        user.set_password(form.password.data)
        db_sess.commit()
        return redirect('/')
    return render_template('profil.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
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
def add_news():
    form = PostForm()
    db_sess = db_session.create_session()
    posts = Posts()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return render_template('post.html',
                                   message="Файл не выбран",
                                   form=form)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            scale_image(input_image_path='static/img/original/' + str(filename),
                        output_image_path='static/img/scaled/' + str(filename),
                        width=800)
            posts.original_f_s_l = 'static/img/original/' + str(filename)
            posts.scaled_f_s_l = 'static/img/scaled/' + str(filename)
            posts.tegs = form.tegs.data
            posts.about = form.about.data
            posts.is_private = form.is_private.data
            current_user.posts.append(posts)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
    return render_template('post.html', title='Добавление работы',
                           form=form)


@app.route('/download/<int:id>')
def download_file(id):
    db_sess = db_session.create_session()
    post_download = db_sess.query(Posts).filter(Posts.id == id).first()
    return send_file(post_download.original_f_s_l)


@app.route('/job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = JobForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                          (Jobs.user == current_user) | (current_user.id == 1)
                                          ).first()
        if jobs:
            form.job_name.data = jobs.job_name
            form.team_leader.data = jobs.team_leader
            form.work_size.data = jobs.work_size
            form.collaborators.data = jobs.collaborators
            form.is_finished.data = jobs.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                          (Jobs.user == current_user) | (current_user.id == 1)
                                          ).first()
        if jobs:
            jobs.job_name = form.job_name.data
            jobs.team_leader = form.team_leader.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('post.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                      (Jobs.user == current_user) | (current_user.id == 1)
                                      ).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
