from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class ProfilForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    username = StringField('Никнейм', validators=[DataRequired()])
    about = TextAreaField('Немного о себе', validators=[DataRequired()])
    submit = SubmitField('Сохранить', validators=[DataRequired()])
