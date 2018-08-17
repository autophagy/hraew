# -*- coding: utf-8 -*-

from flask import Flask, abort, render_template
from .leomu import leomu, faereld_data, faereldSummary
from .utils import format_timedelta

VERSION = '0.1.0'

application = Flask(__name__, static_folder='faestlic', template_folder='bisena')

@application.route("/")
def index():
    return render_template('index.html', lim_key='index',
                                          lim=leomu['index'],
                                          leomu=leomu,
                                          dailyTimes=faereldSummary.get_statistic("index", "total daily times"))

@application.route("/<lim_key>/")
def lim(lim_key):
    if lim_key in leomu:
        return render_template('lim.html', lim_key=lim_key,
                                              lim=leomu[lim_key],
                                              faereld_data=faereld_data.get(lim_key))
    else:
        abort(404)

@application.route("/.well-known/dat")
def dat_well_known():
  return application.send_static_file('regolas/dat')

@application.errorhandler(404)
def pageNotFound(error):
    return render_template('gedwola.html', error_code='404', error_message='Not Found'), 404

@application.errorhandler(500)
def internalServerError(error):
    return render_template('gedwola.html', error_code='500', error_message='Internal Server Error'), 500

@application.context_processor
def inject_version():
    return dict(version=VERSION)

@application.template_filter('format_timedelta')
def format_timedelta_filter(delta):
  return format_timedelta(delta)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
