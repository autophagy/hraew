# -*- coding: utf-8 -*-

from flask import Flask
application = Flask(__name__)

@application.route("/")
def index():
    return "Wilcume on Hrǽw."

if __name__ == "__main__":
    application.run(host='0.0.0.0')
