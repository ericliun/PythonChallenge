import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                        os.path.join(basedir, 'database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.secret_key = 'codepku'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    address = db.Column(db.String(50), nullable=True)
    info = db.Column(db.String(100), nullable=True)
    stage = db.Column(db.Integer, default='0')
    real_avatar = db.Column(db.String(100), default='/static/avatar/code.png')


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', backref=db.backref('posts'))

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post = db.relationship('Post', backref=db.backref('comments'))
    author = db.relationship('User', backref=db.backref('comments'))


class Challenge(db.Model):
    __tablename__ = 'challenge'
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)


class UserForm(FlaskForm):
    username = StringField('用户名:', validators=[DataRequired()])
    password = PasswordField('密码:', validators=[DataRequired()])
    comfirm = PasswordField('确认密码:', validators=[DataRequired()])
    submit = SubmitField('立即注册')


class LoginForm(FlaskForm):
    username = StringField('用户名:', validators=[DataRequired()])
    password = PasswordField('密码:', validators=[DataRequired()])
    submit = SubmitField('登录')


class InfoForm(FlaskForm):
    avatar = FileField('头像')
    email = StringField('邮箱:')
    address = StringField('地址:')
    info = TextAreaField('个人简介:')
    submit = SubmitField('提交信息')


class PostForm(FlaskForm):
    title = StringField('请输入标题:', validators=[DataRequired()])
    content = TextAreaField('请输入内容;', validators=[DataRequired()])
    submit = SubmitField('发布')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if request.method == 'GET':
        return render_template('register.html', form=form)
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
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
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
    posts = Post.query.filter(User.id == user_id).all()
    count = len(posts)
    return render_template(
        'user_detail.html',
        user=user,
        posts=posts,
        count=count)


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

        avatar = request.files['avatar']
        if avatar:
            fname = secure_filename(avatar.filename)
            UPLOAD_FOLDER = os.path.join(basedir, '\\static\\avatar')
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
            # app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
            flag = '.' in fname and fname.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
            if not flag:
                flash('文件类型错误!')
                return redirect((url_for('edit_info', user_id=user.id)))
            avatar.save(os.path.join(basedir, 'static\\avatar\\{}'.format(fname)))
            user.real_avatar = '/static/avatar/{}'.format(fname)
        if email:
            user.email = email
        if address:
            user.address = address
        if info:
            user.info = info
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_detail', user_id=user.id))


@app.route('/forum_index')
def forum_index():
    posts = Post.query.all()
    return render_template('forum_index.html', posts=posts)


@app.route('/post', methods=['GET', 'POST'])
def post():
    if session.get('user_id'):
        form = PostForm()
        if request.method == 'GET':
            return render_template('post.html', form=form)
        else:
            title = request.form.get('title')
            content = request.form.get('content')
            post = Post(title=title, content=content)
            post.author_id = session.get('user_id')
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('forum_index'))
    else:
        return redirect(url_for('login'))


@app.route('/detail/<post_id>')
def detail(post_id):
    post = Post.query.filter(Post.id == post_id).first()
    return render_template('detail.html', post=post)


@app.route('/comment/', methods=['GET', 'POST'])
def comment():
    content = request.form.get('comment_content')
    post_id = request.form.get('post_id')
    print(content, post_id)
    comment = Comment(content=content, post_id=post_id)
    comment.author_id = session.get('user_id')
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail', post_id=post_id))


@app.route('/challenge/<answer>')
def challenge(answer):
    chapter = Challenge.query.filter(Challenge.answer == answer).first()
    if chapter:
        photo = chapter.photo
        chapter_id = chapter.id
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            user.stage = answer
            db.session.commit()
        return render_template('challenge.html', chapter_id=chapter_id, photo=photo)
    else:
        return "<h2>答案错误,请返回重新尝试!</h2>"


if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    # c1 = Challenge(answer='0', photo='challenge.png')
    # c2 = Challenge(answer='challenge', photo='abcde.png')
    # c3 = Challenge(answer='21978', photo='digitnum.png')
    # c4 = Challenge(answer='381654729', photo='joseph.png')
    # db.session.add_all([c1, c2, c3, c4])
    # db.session.commit()
    app.run(debug=True)
