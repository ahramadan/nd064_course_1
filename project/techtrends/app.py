import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys


#Connection Counter
conn_counter =0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global conn_counter
    conn_counter += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

def get_post_count():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(1) FROM posts').fetchone()[0]
    connection.close()
    return post_count
# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('Article with id %s is not found!',str(post_id))
      return render_template('404.html'), 404
    else:
      app.logger.info('Article %s retrieved!',str(post['title']))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page is retrieved!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('New Article %s created!',str(title))
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def status():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Status request successfull')
    app.logger.debug('DEBUG message')

    return response

@app.route('/metrics')
def metrics():

    post_count = get_post_count()
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count": conn_counter, "post_count": post_count}}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Metrics request successfull')

    return response

# start the application on port 3111
if __name__ == "__main__":
   #add logging
    fh = logging.FileHandler('app.log')
    logging.basicConfig(
            level=logging.DEBUG,
            format=
            '%(levelname)s: %(asctime)s.%(msecs)d - [%(threadName)s] %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S',
            handlers=[fh, logging.StreamHandler(sys.stdout)]
    )
    app.run(host='0.0.0.0', port='3111')
