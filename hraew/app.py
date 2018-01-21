# -*- coding: utf-8 -*-

from flask import Flask, abort, render_template
from .entries import entries

application = Flask(__name__, static_folder='faestlic', template_folder='bisena')

@application.route("/")
def index():
    return render_template('layout.html', entry=entries['index'])

@application.route("/<entry>")
def entry(entry):
    if entry in entries:
        return render_template('layout.html', entry=entries[entry])
    else:
        abort(404)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
