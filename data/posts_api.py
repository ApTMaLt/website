import os

import flask
from flask import jsonify, request
from . import db_session
from .posts import Posts
from .users import User

blueprint = flask.Blueprint(
    'posts_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/posts')
def get_posts():
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).all()
    return jsonify(
        {
            'posts':
                [item.to_dict(only=('id', 'tegs', 'about', 'original_img', 'scaled_img', 'user.surname', 'user.name',
                                    'user.username'))
                 for item in posts]
        }
    )


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'name', 'surname', 'email', 'username', 'created_date', 'about',
                                    'posts.id', 'posts.tegs', 'posts.about', 'posts.original_img', 'posts.scaled_img'))
                 for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>')
def get_user(user_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(user_id)
    return jsonify(
        {
            'user':
                users.to_dict(only=('id', 'name', 'surname', 'email', 'username', 'created_date', 'about',
                                    'posts.id', 'posts.tegs', 'posts.about', 'posts.original_img', 'posts.scaled_img'))
        }
    )


@blueprint.route('/api/posts/<int:posts_id>', methods=['DELETE'])
def delete_posts(posts_id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).get(posts_id)
    if not posts:
        return jsonify({'error': 'Not found'})
    if posts:
        if os.path.isfile(posts.original_f_s_l):
            os.remove(posts.original_f_s_l)
            print("success")
        else:
            print("File doesn't exists!")
        if os.path.isfile(posts.scaled_f_s_l):
            os.remove(posts.scaled_f_s_l)
            print("success")
        else:
            print("File doesn't exists!")
    db_sess.delete(posts)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/posts/<int:news_id>', methods=['GET'])
def get_one_post(news_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).get(news_id)
    if not post:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'post':
                post.to_dict(only=('id', 'tegs', 'about', 'original_img', 'scaled_img', 'user.surname', 'user.name',
                                   'user.username'))

        }
    )
