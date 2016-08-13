from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import abort
from flask import flash
from flask import session

# import uuid

from models import User
from models import Todo

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
    u = User(request.form)
    user = User.query.filter_by(username=u.username).first()
    print(user)
    if u.validate(user):
        print(user.username, '登录成功')
        # cookie_id = str(uuid.uuid4())
        # cookie_dict[cookie_id] = user
        session['user_id'] = user.id
        r = redirect(url_for('timeline_view', username=u.username))
        # r.set_cookie('cookie_id', cookie_id)
        return r
    else:
        flash('用户登录失败，请检查密码或账户')
        print(user, '登录失败')
        return redirect(url_for('login_view'))


@app.route('/register')
def register_view():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    u = User(request.form)
    if u.valid(request.form):
        print(u.username, '用户注册成功')
        u.save()
        return redirect(url_for('login_view'))
    else:
        print('注册失败', request.form)
        flash('注册失败，密码长度3位数以上')
        return redirect(url_for('register_view'))


@app.route('/timeline/<username>')
def timeline_view(username):
    u = User.query.filter_by(username=username).first()
    all_users = User.query.all()
    rest = [others for others in all_users if others != u]
    print('这是rest', rest)
    # rest把除了自身以外的其他user展示出来
    # all_users = User.select()
    if all_users is None:
        abort(404)
    else:
        todos = u.todos
        todos.sort(key=lambda t: t.created_time, reverse=True)
        if u.is_admin():
            return render_template('timeline_admin.html', todos=todos, users=rest, user=current_user())
        else:
            return render_template('timeline.html', todos=todos, user=current_user())


@app.route('/todo/add', methods=['POST'])
def todo_add():
    user = current_user()
    if user is None:
        return redirect(url_for('login_view'))
    else:
        t = Todo(request.form)
        t.user = user
        t.save()
        return redirect(url_for('timeline_view', username=user.username))


@app.route('/todo/check/<username>')
def admin_check_user_todo(username):
    u = User.query.filter_by(username=username).first()
    todos = u.todos
    todos.sort(key=lambda t: t.created_time, reverse=True)
    return render_template('timeline.html', todos=todos, user=u)
# 这里return了user=u保证了输入框上方显示的是普通用户，而不是管理员的信息


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