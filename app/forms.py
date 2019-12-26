from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, IntegerField, DecimalField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
from app.models import User, CATEGS


class LoginForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня!', default=False)
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторить пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Это имя уже занято.')


class EditProfileForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль')
    password2 = PasswordField('Повторить пароль',
                              validators=[EqualTo('password')])
    submit = SubmitField('Изменить')


class TransactionForm(FlaskForm):

    day = IntegerField('Когда', validators=[NumberRange(min=1, max=31)])
    desc = StringField('Что')
    categ = SelectField(u'Какое',
                        choices=[(x, x) for x in CATEGS],
                        )
    org = StringField('Где')
    op = SelectField(u'+/-',
                     choices=[(-1, '-'),
                              (1, '+')],
                     coerce=int)

    sum = DecimalField('Сколько', validators=[DataRequired(), NumberRange(min=0.01)])

    submit = SubmitField('Внести')


