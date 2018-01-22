# -*- coding: utf-8 -*-

from flask import Flask, abort, render_template
from .trametas import trametas

VERSION = '0.1.0'

application = Flask(__name__, static_folder='faestlic', template_folder='bisena')

@application.route("/")
def index():
    return render_template('tramet.html', tramet_key='index',
                                          tramet=trametas['index'])

@application.route("/<tramet_key>")
def tramet(tramet_key):
    if tramet_key in trametas:
        return render_template('tramet.html', tramet_key=tramet_key,
                                              tramet=trametas[tramet_key])
    else:
        abort(404)

@application.context_processor
def inject_version():
    return dict(version=VERSION)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
