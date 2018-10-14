from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloglife@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'aw129ifqa0fjpr'

# Blog Class will initialize DB for holding and retreiving blog post


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    # Owner_id will relate blog post to the user that created it
    onwer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

# Blog Class will initialize DB for holding and retrieving User blog post


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():

    allowed_routes = ['login', 'signup', 'blog', 'logout', 'index']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blog_id = request.args.get('id')
    user_id = request.args.get('user')

    blogs = Blog.query.all()
    users = User.query.all()

    if blog_id is not None:
        blogs = Blog.query.filter_by(id=blog_id)
        for blog in blogs:
            username = blog.id
            users = User.query.filter_by(id=username).first()
        return render_template('blogpost.html', blogs=blogs, users=users)
    elif user_id is not None:
        users = User.query.filter_by(username=user_id)
        for user in users:
            user = user.id
            blogs = Blog.query.filter_by(onwer_id=user)
        return render_template('userposts.html', users=users, blogs=blogs)
    else:
        return render_template('blog.html', blogs=blogs, users=users)


@app.route('/newpost', methods=['POST', "GET"])
def newpost():

    title_error = ''
    body_error = ''

    error_check = False

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        user = User.query.filter_by(username=session['user']).first()
        #user = session['user']

        if blog_title == '':
            title_error = 'Please fill in the title'
            error_check = True

        if blog_body == '':
            body_error = 'Please fill in the body'
            error_check = True

        if error_check == False:
            new_blog = Blog(blog_title, blog_body, user)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
        else:
            return render_template('newpost.html',
                                   title=blog_title,
                                   body=blog_body,
                                   title_error=title_error,
                                   body_error=body_error)
    else:
        return render_template('newpost.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data
        username_error = ''
        password_error = ''
        verify_error = ''

        error_check = False

        if validate_test(username):
            username_error = "That's not a valid username"
            error_check = True

        if validate_test(password):
            password_error = "That's not a valid password"
            error_check = True

        if password != verify:
            verify_error = "Passwords don't match"
            error_check = True

        if error_check == False:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['user'] = username
                return redirect('/newpost')
            else:
                # TODO - better response message
                return "<h1>Duplicate User</h1>"
        else:
            return render_template('/signup.html',
                                   username_error=username_error,
                                   password_error=password_error,
                                   verify_error=verify_error,
                                   username=username)

    return render_template('/signup.html')


def validate_test(test):
    if " " in test:
        return True
    else:
        if len(test) < 3 or len(test) > 20:
            return True
        else:
            return False


def validate_password(password, confirm_password):
    return (password == confirm_password)


def validate_email(email):
    if "@" and "." not in email:
        return True
    if len(email) > 20:
        return True
    else:
        return False


def input_blank(test):
    if test == '':
        return True
    else:
        return False


@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exits', 'error')

    return render_template('/login.html')


@app.route('/logout', methods=['GET'])
def logout():

    session.pop('user', None)
    return redirect('/blog')


if __name__ == '__main__':
    app.run()
