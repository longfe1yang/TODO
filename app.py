from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import abort
from flask import session
from flask import jsonify

from models import User
from models import Todo

from my_log import log

app = Flask(__name__)
app.secret_key = 'long'
cookie_dict = {}


def current_user():
    try:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        return user
    except KeyError:
        return None


@app.route('/')
def index():
    return redirect(url_for('login_view'))


@app.route('/login')
def login_view():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    account = request.get_json()
    log('account', account)
    u = User(account)
    user = User.query.filter_by(username=u.username).first()
    log('user的id', user)
    status, msgs, url = u.validate(user)
    r = {
        'success': status,
        'url': url,
        'data': msgs
    }
    if status:
        log(user.username, '登录成功')
        session['user_id'] = user.id
    return jsonify(r)


@app.route('/register')
def register_view():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    account = request.get_json()
    log('注册的account', account)
    u = User(account)
    r = {
        'success': True,
        'url': '/login',
    }
    status, msgs = u.valid()
    if status:
        u.save()
        r['message'] = msgs
        log(r['message'])
    else:
        r['success'] = False
        r['message'] = msgs
        r['url'] = '/register'
        log('else中的', r['message'])
    return jsonify(r)


@app.route('/timeline/<user_id>', methods=['GET'])
def timeline(user_id):
        # todo 权限验证
        u = User.query.filter_by(id=user_id).first()
        # u = current_user()
        log('timeline', u)
        todos = u.todos
        log('log', todos)
        r = dict(
            success=True,
            data=[t.json() for t in todos]
        )
        log('debug r', r)
        return jsonify(r)


@app.route('/timeline')
def timeline_view():
    u = current_user()
    return render_template('timeline.html', user=u)


@app.route('/todo/add', methods=['POST'])
def tweet_add():
    user = current_user()
    # if user is None:
    #     return redirect(url_for('login_view'))
    # else:
    form = request.get_json()
    t = Todo(form)
    t.user = user
    t.save()
    j = t.json()
    print('debug', j)
    r = {
        'success': True,
        'data': j,
    }
    return jsonify(r)


@app.route('/todo/update/<todo_id>')
def todo_update_view(todo_id):
    t = Todo.query.filter_by(id=todo_id).first()
    if t is None:
        abort(404)
    user = current_user()
    if user is None or user.id != t.user.id:
        abort(401)
    else:
        return render_template('todo_edit.html', todo=t)


@app.route('/todo/update/<todo_id>', methods=['POST'])
def todo_update(todo_id):
    t = Todo.query.filter_by(id=todo_id).first()
    if t is None:
        abort(404)
    user = current_user()
    if user is None or user.id != t.user_id:
        abort(404)
    else:
        t.content = request.form.get('content', '')
        t.save()
        return redirect(url_for('timeline_view', username=user.username))


@app.route('/todo/delete/<todo_id>')
def todo_delete(todo_id):
    t = Todo.query.filter_by(id=todo_id).first()
    if t is None:
        abort(404)
    user = current_user()
    if user is None or user.id != t.user_id:
        abort(401)
    else:
        t.delete()
        return redirect(url_for('timeline_view', username=user.username))


@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('login_view'))

if __name__ == '__main__':
    app.run(debug=True)
    # host, port = '0.0.0.0', 13000
    # args = {
    #      'host': host,
    #      'port': port,
    #      'debug': True,
    #  }
    # app.run(**args)