from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:cheese@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    if blog_id is not None:
        blogs = Blog.query.filter_by(id=blog_id)
        return render_template('blogpost.html', blogs=blogs)
    else:    
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)


@app.route('/newpost', methods=['POST', "GET"])
def newpost():
    title_error = ''
    body_error = ''

    error_check = False

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        if blog_title == '':
            title_error = 'Please fill in the title'
            error_check = True

        if blog_body == '':
            body_error = 'Please fill in the body'
            error_check = True

        if error_check == False:
            new_blog = Blog(blog_title, blog_body)
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


if __name__ == '__main__':
    app.run()
