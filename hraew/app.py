# -*- coding: utf-8 -*-

from flask import Flask, abort, render_template
from .leomu import leomu

VERSION = '0.1.0'

application = Flask(__name__, static_folder='faestlic', template_folder='bisena')

@application.route("/")
def index():
    return render_template('lim.html', lim_key='index',
                                          lim=leomu['index'])

@application.route("/<lim_key>")
def lim(lim_key):
    if lim_key in leomu:
        return render_template('lim.html', lim_key=lim_key,
                                              lim=leomu[lim_key])
    else:
        abort(404)

@application.errorhandler(404)
def pageNotFound(error):
    return render_template('gedwola.html', error_code='404', error_message='Not Found'), 404

@application.errorhandler(500)
def internalServerError(error):
    return render_template('gedwola.html', error_code='500', error_message='Internal Server Error'), 500

@application.context_processor
def inject_version():
    return dict(version=VERSION)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
