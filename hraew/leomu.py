# -*- coding: utf-8 -*-
from os.path import dirname, join, splitext
from os import listdir
import bleach
import re
from flask import url_for, render_template
import wisdomhord
import datetime as dt
import datarum
from math import floor

import wisdomhord
from wisdomhord import Bisen, Sweor

from .parser import Parser
from .faereld import FaereldService

from .limspraec_raedere import LimspræcRædere


class Lim(object):

    _body_html = None

    def __init__(self, key, lim):
        self.key = key
        self.name = lim.get("name", "")
        self.brief = lim.get("brief", "")
        self.project = lim.get("project", False)
        self.status = lim.get("status", "n/a")
        self.head = lim.get("head", "")
        self.body = lim.get("body", "")
        self.externals = lim.get("externals", None)
        self.bleoh = lim.get("bleoh", "deorc")

    def to_html(self):
        if self._body_html is None:
            parser = Parser(self.key, self.body, faereldService)
            self._body_html = parser.render_html()

        return self._body_html

leomu = {}
raedere = LimspræcRædere()
for f in listdir(join(dirname(__file__), "leomu")):
    _, ext = splitext(f)
    if ext == ".lim":
        raed_leomu = raedere.raed(join(dirname(__file__), "leomu", f))
        for key, value in raed_leomu.items():
            leomu[key] = Lim(key, value)

project_areas = ["RES", "DES", "DEV", "DOC", "TST"]

faereldService = FaereldService(leomu.keys(), project_areas, "horda/faereld.hord")
