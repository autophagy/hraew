# -*- coding: utf-8 -*-
import yaml
from os.path import dirname, join
import bleach
import re
from flask import url_for, render_template
import wisdomhord
import datetime as dt
from math import floor

import wisdomhord
from wisdomhord import Bisen, Sweor

from .parser import Parser


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

    def to_html(self):
        if self._body_html is None:
            parser = Parser(self.key, self.body)
            self._body_html = parser.render_html()

        return self._body_html


class FaereldLim(object):

    PROJECT_AREAS = ["RES", "DES", "DEV", "DOC", "TST"]

    def __init__(self, faereld_data):
        self.populate_stats(faereld_data)

    def populate_stats(self, faereld_data):
        # We need the percentages of areas for the bars, as well as first entry,
        # last entry and the total time.

        first_entry = None
        last_entry = None
        self.total_time = dt.timedelta()

        area_time_map = dict(map(lambda x: (x, dt.timedelta()), self.PROJECT_AREAS))

        for row in faereld_data:
            start = row["START"]
            end = row["END"]

            if first_entry is None:
                first_entry = start
            if last_entry is None:
                last_entry = end

            if start < first_entry:
                first_entry = start

            if start > last_entry:
                last_entry = start

            self.total_time += end - start

            if area_time_map.get(row["AREA"]) is None:
                area_time_map[row["AREA"]] = end - start
            else:
                area_time_map[row["AREA"]] += end - start

        self.percentages = dict(
            map(
                lambda x: (x[0], x[1] / max(area_time_map.values())),
                area_time_map.items(),
            )
        )
        self.first_entry = first_entry.strftime("{daeg} {month} {gere}")
        self.last_entry = last_entry.strftime("{daeg} {month} {gere}")

    def formatted_total_time(self):
        hours, remainder = divmod(self.total_time.total_seconds(), 3600)
        minutes = floor(remainder / 60)

        return "{0}h{1}m".format(floor(hours), minutes)


class FaereldBisen(Bisen):

    __invoker__ = "Færeld"
    __description__ = "Productive task time tracking data produced by Færeld"

    col1 = Sweor("AREA", wisdomhord.String)
    col2 = Sweor("OBJECT", wisdomhord.String)
    col3 = Sweor("START", wisdomhord.Wending)
    col4 = Sweor("END", wisdomhord.Wending)


def get_projects_faereld_data(faereld_rows):
    faereld_data = {}
    faereld_leomu = {}

    for row in faereld_rows:
        if faereld_data.get(row["OBJECT"]) is None:
            faereld_data[row["OBJECT"]] = [row]
        else:
            faereld_data[row["OBJECT"]].append(row)

    for k, v in faereld_data.items():
        faereld_leomu[k] = FaereldLim(v)

    return faereld_leomu


with open(join(dirname(__file__), "leomu/leomu.yml"), "r") as leomu_yml:
    leomu = yaml.load(leomu_yml)
    for key, value in leomu.items():
        leomu[key] = Lim(key, value)

hord = wisdomhord.hladan(
    join(dirname(__file__), "faereld/faereld.hord"), bisen=FaereldBisen
)

project_areas = ["RES", "DES", "DEV", "DOC", "TST"]

faereld_data = get_projects_faereld_data(
    hord.get_rows(
        filter_func=lambda x: x["AREA"] in project_areas and x["OBJECT"] in leomu.keys()
    )
)
