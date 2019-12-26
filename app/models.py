from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from hashlib import md5

MONTHS = ('0',
          'январь',
          'февраль',
          'март',
          'апрель',
          'май',
          'июнь',
          'июль',
          'август',
          'сентябрь',
          'октябрь',
          'ноябрь',
          'декабрь')

CATEGS = ('Без категории',
          'Большая покупка',
          'Доход',
          'Обязательное',
          'Продукты',
          'Питание',
          'Быт',
          'Развлечения',
          'Транспорт',
          'Подарки')


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, index=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=False, index=True)

    transactions = db.relationship('Transaction', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=retro&s={}'.format(
            digest, size)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    date = db.Column(db.Date, nullable=False, default=datetime.date.today())
    desc = db.Column(db.String(140), default='Загадочная транзакция')
    categ = db.Column(db.String(50), default='Без категории')
    org = db.Column(db.String(140), default='???')
    sum = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<%s: Transaction %r>' % self.date, self.desc
