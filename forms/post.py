from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    file = FileField('Фото')
    tegs = StringField('Теги', validators=[DataRequired()])
    about = StringField('Описание (необязательно)', validators=[DataRequired()])
    is_private = BooleanField("Личное")
    submit = SubmitField('Опубликовать')