from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    from datetime import datetime
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %X")
    return "Hello, Flask! It's now %s." % formatted_now

if __name__ == "__main__":
    app.run()
