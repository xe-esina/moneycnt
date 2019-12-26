# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from sqlalchemy import extract, func
from app import app, db
from app.models import User, Transaction, MONTHS, CATEGS
from .forms import LoginForm, RegisterForm, TransactionForm, EditProfileForm
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import datetime


# Главный адрес
# Перенаправляет на /login, /admin, /counter
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        if current_user.username == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('counter'))

    return redirect(url_for('login'))


# Авторизация
# Вход в аккаунт или переход к регистрации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.username == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('counter'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        if user.username == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('counter'))

    return render_template('login.html',
                           title='Вход',
                           form=form)


# Выход из аккаунта
# Выходит и пересылает на логин
@app.route('/logout/')
def logout():
    logout_user()
    flash("Вы успешно вышли из аккаунта.")
    return redirect(url_for('login'))


# Регистрация
# Форма регистрации с редиректом на логин
# Можно зарегаться только как юзер
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(username=form.username.data)

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Вы зарегистрировались! Теперь можно входить.')
        return redirect(url_for('login'))

    return render_template('register.html',
                           title='Регистрация',
                           form=form)


# Редактирование профиля (для владельца или админа)
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    profile_id = request.args.get("id", current_user.id, type=int)
    u = User.query.filter(User.id == profile_id).first()

    form = EditProfileForm()
    if form.validate_on_submit():
        u.username = form.username.data

        if form.password.data != '':
            u.set_password(form.password.data)

        db.session.commit()

        flash('Ваши изменения сохранены!')
        return redirect(url_for('profile', id=profile_id))
    elif request.method == 'GET':
        form.username.data = u.username
        form.password.data = ''

    return render_template("profile.html",
                           title='Редактировать профиль',
                           user=u,
                           form=form)


# Админка (только для админов)
# Позволяет просматривать инфу о пользователях и удалять профили
@login_required
@app.route('/admin')
def admin():
    if current_user.username != 'admin':
        return redirect(url_for('counter'))

    delete_id = request.args.get('delete', -1, type=int)
    if delete_id > -1:
        u = User.query.filter(User.id == delete_id).first()

        for t in u.transactions.all():
            db.session.delete(t)

        db.session.delete(u)
        db.session.commit()

        flash('Пользователь удален!')
        return redirect(url_for('admin'))

    users_list = User.query.all()

    return render_template('admin.html',
                           title='Админка',
                           user=current_user,
                           users_list=users_list)


# Считалка (только для пользователей)
# Денежная таблица с фильтрами и wysiwyg-редактированием
@login_required
@app.route('/counter', methods=['GET', 'POST'])
def counter():
    if current_user.username == 'admin':
        return redirect(url_for('admin'))

    month = request.args.get('month', datetime.date.today().month, type=int)
    year = request.args.get('year', datetime.date.today().year, type=int)
    delete_trans_id = request.args.get('delete', -1, type=int)
    edit_id = request.args.get('edit', -1, type=int)

    # Удалить запись
    if delete_trans_id != -1:
        t = Transaction.query.filter(Transaction.id == delete_trans_id).first()
        db.session.delete(t)
        db.session.commit()

        flash('Запись удалена!')
        return redirect(url_for('counter', month=month, year=year))

    # Заполнение формы
    form = TransactionForm()

    if request.method == 'GET' and edit_id > -1:
        t = Transaction.query.filter(Transaction.id == edit_id).first()

        form.day.data = int(t.date.day)
        form.desc.data = str(t.desc)
        form.categ.data = str(t.categ)
        form.org.data = str(t.org)
        form.op.data = int(t.sum / abs(t.sum))
        form.sum.data = int(abs(t.sum))

    # Внести запись в БД
    if form.validate_on_submit():
        t = Transaction()

        if edit_id > -1:
            t = Transaction.query.filter(Transaction.id == edit_id).first()

        t.user_id = current_user.id
        t.date = datetime.date(year, month, form.day.data)
        t.desc = form.desc.data
        t.categ = form.categ.data
        t.org = form.org.data
        t.sum = int(form.op.data) * int(form.sum.data)

        db.session.add(t)
        db.session.commit()

        flash('Запись добавлена!' if edit_id == -1 else 'Запись изменена!')
        return redirect(url_for('counter', month=month, year=year))

    # Обработка пагинации по месяцам
    cur_month_word = MONTHS[month].capitalize()
    cur = [month, year]
    prev = [month - 1, year] if month > 1 else [12, year - 1]
    next = [month + 1, year] if month < 12 else [1, year + 1]

    trans = current_user.transactions.filter(
        extract('month', Transaction.date) == month and extract('year', Transaction.date) == year).order_by(
        Transaction.date.desc())
    return render_template('counter.html',
                           title='Деньги',
                           user=current_user,
                           trans=trans,
                           cur=cur,
                           prev=prev,
                           next=next,
                           cur_month_word=cur_month_word,
                           form=form)


@login_required
@app.route('/globalstats')
def globalstats():
    # Определяем месяц
    month = request.args.get('month', datetime.date.today().month, type=int)
    year = request.args.get('year', datetime.date.today().year, type=int)

    cur_month_word = MONTHS[month].capitalize()
    cur = [month, year]
    prev = [month - 1, year] if month > 1 else [12, year - 1]
    next = [month + 1, year] if month < 12 else [1, year + 1]

    data = {'Категория': 'Сумма за месяц'}

    for c in CATEGS:
        s = str(db.session.query(func.sum(-1 * Transaction.sum).label('sum')
                    ).filter(extract('month', Transaction.date) == month and extract('year', Transaction.date) == year
                    ).filter(Transaction.categ == c).group_by(Transaction.categ).first()).replace('(', '').replace(')', '').replace(',', '')

        if s != 'None':
            data[c] = int(s)

    # if data
    # data.pop('Доход')
    print(data)

    return render_template('globalstats.html',
                           title='Статистика',
                           user=current_user,
                           data=data,
                           cur=cur,
                           prev=prev,
                           next=next,
                           cur_month_word=cur_month_word
                           )


@login_required
@app.route('/stats')
def stats():
    # Определяем месяц
    month = request.args.get('month', datetime.date.today().month, type=int)
    year = request.args.get('year', datetime.date.today().year, type=int)

    cur_month_word = MONTHS[month].capitalize()
    cur = [month, year]
    prev = [month - 1, year] if month > 1 else [12, year - 1]
    next = [month + 1, year] if month < 12 else [1, year + 1]

    data = {'Категория': 'Сумма за месяц'}

    for c in CATEGS:
        s = str(db.session.query(func.sum(-1 * Transaction.sum).label('sum')
                    ).filter(Transaction.user_id == current_user.id
                    ).filter(extract('month', Transaction.date) == month and extract('year', Transaction.date) == year
                    ).filter(Transaction.categ == c).group_by(Transaction.categ).first()).replace('(', '').replace(')', '').replace(',', '')

        if s != 'None':
            data[c] = int(s)

    # if data
    # data.pop('Доход')
    print(data)

    return render_template('stats.html',
                           title='Статистика',
                           user=current_user,
                           data=data,
                           cur=cur,
                           prev=prev,
                           next=next,
                           cur_month_word=cur_month_word
                           )
