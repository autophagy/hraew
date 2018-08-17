# -*- coding: utf-8 -*-
import yaml
from os.path import dirname, join
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
            parser = Parser(self.key, self.body)
            self._body_html = parser.render_html()

        return self._body_html


class FaereldIndex(object):

    PROJECT_AREAS = ["RES", "DES", "DEV", "DOC", "TST"]

    def __init__(self, faereld_data):
        self.total_time = dt.timedelta()
        self.total_logs = 0
        self.project_time = dt.timedelta()
        self.project_logs = 0
        self.days = 0
        self.populate_stats(faereld_data)

    def populate_stats(self, faereld_data):
        today = datarum.wending.now()
        earliest = datarum.wending.now()

        for row in faereld_data:
            self.total_time += row.end - row.start
            self.total_logs += 1
            if row.area in self.PROJECT_AREAS:
                self.project_time += row.end - row.start
                self.project_logs += 1
            if row.start < earliest:
                earliest = row.start
        self.days = (today - earliest).days + 1
        self.total_time = self.formatted_time(self.total_time)
        self.project_time = self.formatted_time(self.project_time)

    def formatted_time(self, delta):
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes = floor(remainder / 60)
        return "{0}h{1}m".format(floor(hours), minutes)


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

        today = datarum.wending.now()
        today_ord = today.toordinal()

        area_time_map = dict(map(lambda x: (x, dt.timedelta()), self.PROJECT_AREAS))

        daily_times = [None] * 365

        for i in range(365):
            daily_times[i] = [today - dt.timedelta(i), {}, dt.timedelta()]

        for row in faereld_data:
            start = row.start
            end = row.end

            if 0 <= today_ord - start.toordinal() < 365:
                days = today_ord - start.toordinal()
                if daily_times[days][1].get(row.area) is None:
                    daily_times[days][1][row.area] = end - start
                else:
                    daily_times[days][1][row.area] += end - start
                daily_times[days][2] += end - start

            if first_entry is None:
                first_entry = start
            if last_entry is None:
                last_entry = end

            if start < first_entry:
                first_entry = start

            if start > last_entry:
                last_entry = start

            self.total_time += end - start

            if area_time_map.get(row.area) is None:
                area_time_map[row.area] = end - start
            else:
                area_time_map[row.area] += end - start

        self.percentages = dict(
            map(
                lambda x: (x[0], x[1] / max(area_time_map.values())),
                area_time_map.items(),
            )
        )

        def threshold(delta):
            seconds = delta.total_seconds()
            if seconds >= 90 * 60:
                return "high-activity"
            elif 60 <= seconds < 90 * 60:
                return "medium-activity"
            elif 0 > seconds < 30 * 60:
                return "low-activity"
            return "no-activity"


        self.count = len(faereld_data)
        self.daily_times = list(
            map(lambda x: (x[0], x[1], threshold(x[2])), daily_times)
        )
        self.first_entry = first_entry.strftime("{daeg} {month} {gere}")
        self.last_entry = last_entry.strftime("{daeg} {month} {gere}")


class FaereldBisen(Bisen):

    __invoker__ = "Færeld"
    __description__ = "Productive task time tracking data produced by Færeld"

    area = Sweor("AREA", wisdomhord.String)
    object = Sweor("OBJECT", wisdomhord.String)
    start = Sweor("START", wisdomhord.Wending)
    end = Sweor("END", wisdomhord.Wending)


def get_projects_faereld_data(faereld_rows):
    faereld_data = {}
    faereld_leomu = {}

    for row in faereld_rows:
        if faereld_data.get(row.object) is None:
            faereld_data[row.object] = [row]
        else:
            faereld_data[row.object].append(row)

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
        filter_func=lambda x: x.area in project_areas and x.object in leomu.keys()
    )
)

faereld_index_data = FaereldIndex(hord.get_rows())
