from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpword@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'launchcode'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(450))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = user.username
            flash('Welcome ,' +user.username)
            return redirect('/newpost')
        
        else:
            flash('Username or password is incorrect', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Duplicate user', 'error')
            return render_template('signup.html')

        if len(username) == '' or len(username) < 3:
            flash('Invalid username', 'error')
            return redirect('/signup')
           

        if len(password) == '' or len(password) < 3:
            flash('Invalid password', 'error')
            return redirect('/signup')
           

        if verify != password:
            flash('Passwords do not match', 'error')
            return redirect('/signup')

    return render_template('signup.html')

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    blogs = Blog.query.all()
    users = User.query.all()
    return render_template('index.html', title='Issa Blog', users=users, blogs=blogs)
       
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    user = User.query.filter_by(username=session['username']).first()
    if request.method == 'GET':
        return render_template('newpost.html')
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        if title == '':
           flash("Please fill in the title", 'error')
           return redirect('/newpost')

        if body == '':
            flash("Please fill in the body", 'error')
            return redirect('/newpost')
        else:
            new_post = Blog(title, body, user)
            db.session.add(new_post)
            db.session.commit()
            blog_id = new_post.id
        return redirect('/blog?id=' +str(blog_id))


@app.route('/blog', methods=['POST','GET'])
def blog():
    users = User.query.all()
    blogs = Blog.query.all()
    blog_content = []
    if "id" in request.args:
        blog_id = int(request.args.get('id'))
        blog = Blog.query.get(blog_id)
        user = User.query.filter_by(id=blog.owner_id).first()
        return render_template('blog.html', blog=blog, user=user)
    elif "user" in request.args:
        username = request.args.get('user')
        for user in users:
            print(user.username)
            if user.username == username:
                blog_content = Blog.query.filter_by(user=user).all()
        return render_template('userpage.html', blogs=blog_content, user=user)
    else:
        return render_template('blogpage.html', blogs=blogs)
    



if __name__ == '__main__':
    app.run()