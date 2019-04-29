import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
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

class UserForm(FlaskForm):
    username = StringField('用户名:',validators=[DataRequired()])
    password = PasswordField('密码:', validators=[DataRequired()])
    comfirm = PasswordField('确认密码:', validators=[DataRequired()])
    submit = SubmitField('立即注册')

class LoginForm(FlaskForm):
    username = StringField('用户名:',validators=[DataRequired()])
    password = PasswordField('密码:', validators=[DataRequired()])
    submit = SubmitField('登录')


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
            return redirect(url_for('index'))
        else:
            flash("用户名或密码错误!")
            return redirect(url_for('login'))



@app.route('/')
def index():
    db.drop_all()
    db.create_all()
    return render_template('index.html')

@app.route('/challenge/0')
def zero():
    return render_template('calc.html')

@app.route('/challenge/274877906944')
def map():
    return render_template('map.html')

@app.route('/challenge/cor')
def cor():
    return render_template('cor.html')

if __name__ == '__main__':

    app.run(debug=True)
