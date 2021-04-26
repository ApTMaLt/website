import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Posts(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'posts'
    original_f_s_l = sqlalchemy.Column(sqlalchemy.String)  # original file storage location
    scaled_f_s_l = sqlalchemy.Column(sqlalchemy.String)  # scaled file storage location
    scaled_img = sqlalchemy.Column(sqlalchemy.String)
    original_img = sqlalchemy.Column(sqlalchemy.String)
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_uploud = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"))
    tegs = sqlalchemy.Column(sqlalchemy.String)
    about = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user = orm.relation('User')
