import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

'''
1. 配置数据库
2. 添加用户模型
3. 使用WTF显示登录/注册表单
'''

Bootstrap(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'codepku'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    address = db.Column(db.String(50), nullable=True)
    info = db.Column(db.String(100), nullable=True)


class UserForm(FlaskForm):
    username = StringField('用户名:',validators=[DataRequired()])
    password = PasswordField('密码:', validators=[DataRequired()])
    comfirm = PasswordField('确认密码:', validators=[DataRequired()])
    submit = SubmitField('立即注册')

class LoginForm(FlaskForm):
    username = StringField('用户名:',validators=[DataRequired()])
    password = PasswordField('密码:', validators=[DataRequired()])
    submit = SubmitField('登录')

class InfoForm(FlaskForm):
    email = StringField('邮箱:')
    address = StringField('地址:')
    info = TextAreaField('个人简介:')
    submit = SubmitField('提交信息')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if request.method == 'GET':
        return  render_template('register.html', form=form)
    else:
        username = form.username.data
        password = form.password.data
        comfirm = form.comfirm.data

        user = User.query.filter(User.username == username).first()
        if user:
            flash("该用户名已被注册!")
            return redirect(url_for('register'))
        else:
            if password != comfirm:
                flash("两次密码不相等,请核对后填写!")
                return redirect(url_for('register'))
            else:
                user = User(
                    username=username,
                    password=password)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))

@app.route('/')
def index():
    # db.drop_all()
    db.create_all()
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    else:
        username = form.username.data
        password = form.password.data
        user = User.query.filter(User.username == username).first()
        if user and password == user.password:
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('index'))
        else:
            flash("用户名或密码错误!")
            return redirect(url_for('login'))

@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'um': user}
    return {}

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user_detail/<user_id>')
def user_detail(user_id):
    user = User.query.filter(User.id == user_id).first()
    return render_template('user_detail.html',user=user)


@app.route('/edit_info/<user_id>', methods=['GET', 'POST'])
def edit_info(user_id):
    form = InfoForm()
    user = User.query.filter(User.id == user_id).first()
    if request.method == 'GET':
        return render_template('edit_info.html', form=form)
    else:
        email = form.email.data
        address = form.address.data
        info = form.info.data
        user.email = email
        user.address = address
        user.info = info
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_detail', user_id=user.id))


#########################
@app.route('/challenge/0')
def zero():
    return render_template('calc.html')

@app.route('/challenge/274877906944')
def map():
    return render_template('map.html')

@app.route('/challenge/ocr')
def cor():
    return render_template('ocr.html')

if __name__ == '__main__':

    app.run(debug=True)
