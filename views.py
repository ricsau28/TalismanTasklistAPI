from flask import Flask, render_template, request, session, flash, \
    redirect, url_for, jsonify, g
#from . import app -- if desired, uncomment if deploying to Apache
#from talismansoftwaresolutions import app -- uncomment if deploying locally
from talismansoftwaresolutions import app


@app.route("/")
def index():
    from datetime import datetime
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y %X")
    msg =  "This site is under construction. It's now %s." % formatted_now
    return render_template('index.html', message=msg)

@app.route("/hello")
def hello():
    return "Hello, world. This website is under construction!"

