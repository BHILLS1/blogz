from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:lcbuildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(450))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', title='Build A Blog', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error = ''
        body_error = ''

        if title == '':
           title_error="Please fill in the title"

        if body == '':
            body_error="Please fill in the body"

            
        if title_error or body_error:
            return render_template('newpost.html', body_error=body_error, title_error=title_error)
        else:
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
        return redirect('/')

    return render_template('newpost.html')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
   return render_template('blog.html')




if __name__ == '__main__':
    app.run()