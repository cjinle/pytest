#!/usr/bin/env python

from flask import Flask, abort, redirect, url_for
app = Flask(__name__)

@app.route("/")
def index():
    return "index page"

@app.route("/hello")
def hello():
    return "Hello World!"

@app.route("/404")
def page404():
    app.logger.debug("404 message mark.")
    abort(404)
    
@app.route("/l")
def l():
    return redirect(url_for('index'))

@app.route("/user/<username>")
def show_user_profile(username):
    return "User: %s" % username



if __name__ == "__main__":
    app.run()