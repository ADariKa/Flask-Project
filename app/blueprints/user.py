from flask import Blueprint, render_template, request, flash, make_response, jsonify, url_for, \
    redirect, abort
from flask_login import login_required, login_user, logout_user, current_user
from app import login_manager, api, get_session
from app.models import User
from app.forms import RegisterForm, AuthorizationForm
from app.user_api import UserResource
from app.token import send_confirm_message, confirm_token

import requests
import base64
import datetime

blueprint_user = Blueprint('user', __name__, template_folder='templates')


@login_manager.user_loader
def load_user(user_id):
    return User.get_query().get(user_id)


@blueprint_user.route('/registration', methods=['GET', 'POST'])
def registration():
    register_form = RegisterForm()
    title = 'Регистрация'
    if register_form.validate_on_submit():
        response = requests.post(api.url_for(UserResource, _external=True),
                                 json=request.form.to_dict())
        if response:
            flash('Регистрация прошла успешно', 'success')
            user = User.get_query().get(response.json()['user_id'])
            login_user(user)
            result = send_confirm_message(user)
            if result['status']:
                flash(result['message'], 'warning')
            else:
                flash(result['message'], 'success')
            return make_response(jsonify({
                'redirect': True,
                'redirect_url': url_for('index')
            }), 200)
        else:
            return make_response(jsonify(response.json()), response.status_code)
    elif request.method == 'POST' and not register_form.validate_on_submit():
        errors = {}
        for error in register_form.login.errors:
            errors['login'] = error
        for error in register_form.email.errors:
            errors['email'] = error
        for error in register_form.password.errors:
            errors['password'] = error
        for error in register_form.repeat_password.errors:
            errors['repeat_password'] = error
        if errors:
            return make_response(jsonify({'message': errors}), 400)
    elif request.method == 'GET':
        return render_template('registration.html', register_form=register_form, title=title)


@blueprint_user.route('/confirm/<token>')
@login_required
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        return redirect(url_for('index'))
    user = User.get_query().filter(User.email == email).first_or_404()
    if current_user.email != user.email:
        abort(401)
    if user.confirmed:
        flash('Аккаунт уже подтвержден', 'success')
    else:
        user.confirmed = True
        user.confirmed_date = datetime.datetime.now()
        session = get_session()
        session.commit()
        flash('Учетная запись успешно подтверждена', 'success')
    return redirect(url_for('index'))


@blueprint_user.route('/login', methods=['GET', 'POST'])
def login():
    authorization_form = AuthorizationForm()
    title = 'Авторизация'
    if authorization_form.validate_on_submit():
        login_data = authorization_form.login.data
        password = authorization_form.password.data
        remember = authorization_form.remember.data
        user = User.get_query().filter(User.login == login_data).first()
        if user:
            if user.check_password(password):
                login_user(user, remember=remember)
                return make_response(jsonify({
                    'redirect': True,
                    'redirect_url': url_for('index')
                }), 200)
            return make_response(jsonify({
                'message': {'Ошибка': 'Неверный пароль'}
            }), 400)
        return make_response(jsonify({
            'message': {'Ошибка': 'Пользователь с таким логином не найден'}
        }), 400)
    elif request.method == 'POST' and not authorization_form.validate_on_submit():
        errors = {}
        for error in authorization_form.login.errors:
            errors['login'] = error
        for error in authorization_form.password.errors:
            errors['password'] = error
        if errors:
            return make_response(jsonify({'message': errors}), 400)
    elif request.method == 'GET':
        return render_template('login.html', authorization_form=authorization_form, title=title)


@blueprint_user.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_page(user_id):
    if user_id != int(current_user.get_id()) and current_user.importance != 2:
        flash('У вас нет прав доступа к этому аккаунту', 'error')
        return redirect(url_for('index'))
    user = User.get_query().get(user_id)
    if user:
        if request.method == 'GET':
            return render_template('user.html', user=user)
    abort(401)


@blueprint_user.route('/activate-email')
@login_required
def activate_email():
    result = send_confirm_message(current_user)
    if result['status']:
        return make_response(jsonify(
            {'message': result['message']}), 200)
    else:
        return make_response(jsonify(
            {'message': result['message']}), 200)


@blueprint_user.route('/subscribe')
@login_required
def subscribe():
    user_id = current_user.get_id()
    if current_user.subscription:
        requests.put(api.url_for(UserResource, user_id=user_id, _external=True),
                     json={'subscription': False})
    else:
        requests.put(api.url_for(UserResource, user_id=user_id, _external=True),
                     json={'subscription': True})
    return make_response(jsonify({
        'subscribe_status': current_user.subscription
    }), 200)


@blueprint_user.route('/user-image', methods=['POST'])
@login_required
def user_image():
    data_image = request.form.get('image').split(',', maxsplit=1)
    format_img = data_image[0].split('/')[1].split(';')[0]
    base_64_srt = data_image[1]
    file_content = base64.b64decode(base_64_srt)
    url_file = f'app/static/img/users_avatar/{current_user.get_id()}.{format_img}'
    with open(url_file, mode='wb') as img_file:
        img_file.write(file_content)
    filename = f'img/users_avatar/{current_user.get_id()}.{format_img}'
    user_id = current_user.get_id()
    response = requests.put(api.url_for(UserResource, user_id=user_id, _external=True),
                            json={'image_file': filename})
    if response:
        return make_response(jsonify({'status': 'ok'}), 200)
    else:
        return make_response(jsonify({'status': 'error server'}), 400)


@blueprint_user.route('/edit-user', methods=['POST'])
@login_required
def edit_user():
    old_password = request.form.get('old_password', None)
    if old_password:
        if not current_user.confirmed:
            return make_response(jsonify({
                'message': {'Ошибка': 'Аккаунт не подтвержден'}
            }), 400)
        if not current_user.check_password(old_password):
            return make_response(jsonify({
                'message': {'Ошибка': 'Неверный пароль'}
            }), 400)
    user_id = current_user.get_id()
    response = requests.put(api.url_for(UserResource, user_id=user_id, _external=True),
                            json=request.form.to_dict())
    if response:
        return make_response(jsonify({'message': 'status ok'}), 200)
    else:
        return make_response(jsonify(response.json()), 400)


@blueprint_user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))