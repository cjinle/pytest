#!/usr/bin/env python

from flask import Flask, abort, redirect, url_for
from flask.templating import render_template
app = Flask(__name__)

@app.route("/")
def index():
    return "index page"

@app.route("/hello")
def hello():
    s = 'world'
    l = range(100, 120)
    return render_template('hello2.html', name=s, nums=l)

@app.route("/l")
def l():
    return redirect(url_for('index'))

@app.route("/user/<username>")
def show_user_profile(username):
    return "User: %s" % username



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
