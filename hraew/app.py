# -*- coding: utf-8 -*-

from flask import Flask, abort
from .entries import entries

application = Flask(__name__)

@application.route("/")
def index():
    return entries['index'].to_html()

@application.route("/<entry>")
def entry(entry):
    if entry in entries:
        return entries[entry].to_html()
    else:
        abort(404)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
