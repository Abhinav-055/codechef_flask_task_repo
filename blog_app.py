from flask import Flask, render_template, request, redirect, url_for, session,flash
import re
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
import pytz
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'Abhinav'
db = SQLAlchemy(app)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Kolkata')))
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

@app.route('/')
def home():
    if 'user_id' in session:
        posts = BlogPost.query.all()
        return render_template('home.html', posts=posts)
    else:
        return redirect(url_for('login'))
    
with app.app_context():
    db.create_all()
    
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    return True

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if is_valid_password(password):
            new_user = User(username=username, password=password)  
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('register.html')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user_id' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']

            new_post = BlogPost(title=title, content=content, user_id=session['user_id'])
            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for('home'))

        return render_template('create_post.html')

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
