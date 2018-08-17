from os.path import dirname, join
import wisdomhord
import datetime as dt
import datarum
from math import floor
from .utils import format_timedelta


class FaereldBisen(wisdomhord.Bisen):

    __invoker__ = "Færeld"
    __description__ = "Productive task time tracking data produced by Færeld"

    area = wisdomhord.Sweor("AREA", wisdomhord.String)
    object = wisdomhord.Sweor("OBJECT", wisdomhord.String)
    start = wisdomhord.Sweor("START", wisdomhord.Wending)
    end = wisdomhord.Sweor("END", wisdomhord.Wending)


class FaereldStatics(object):
    _statistic_keys = {}

    def has(self, key):
        return key in self._statistic_keys

    def get(self, key):
        return self._statistic_keys.get(key)()

    def __str__(self):
        s = []
        for k, v in self._statistic_keys.items():
            s.append(k + " : " + str(v()))
        return "\n".join(s)


class GeneralStatistics(FaereldStatics):
    def __init__(self):
        self.total_time = dt.timedelta()
        self.total_logs = 0
        self.total_project_time = dt.timedelta()
        self.total_project_logs = 0
        self.incept_date = datarum.wending.now()

        self._statistic_keys = {
            "total time": lambda: format_timedelta(self.total_time),
            "total logs": lambda: self.total_logs,
            "total project time": lambda: format_timedelta(self.total_project_time),
            "total project logs": lambda: self.total_project_logs,
            "incept date": lambda: self.incept_date.strftime("{daeg} {month} {gere}"),
            "days since incept": lambda: self.days_since_incept,
        }

    def update(self, entry, project_areas):
        self.total_time += entry.end - entry.start
        self.total_logs += 1
        if entry.start < self.incept_date:
            self.incept_date = entry.start
        if entry.area in project_areas:
            self.total_project_time += entry.end - entry.start
            self.total_project_logs += 1

    @property
    def days_since_incept(self):
        assert isinstance(self.incept_date, datarum.wending)
        return (datarum.wending.now() - self.incept_date).days + 1


class LimStatistics(FaereldStatics):
    class DailyTime(object):
        def __init__(self, date):
            self.date = date
            self.area_time_map = {}
            self.total_time = dt.timedelta()

        def update(self, entry):
            if entry.area in self.area_time_map:
                self.area_time_map[entry.area] += entry.end - entry.start
            else:
                self.area_time_map[entry.area] = entry.end - entry.start
            self.total_time += entry.end - entry.start

        @property
        def activity(self):
            seconds = self.total_time.total_seconds()
            if seconds >= 90 * 60:
                return "high-activity"
            elif 60 <= seconds < 90 * 60:
                return "medium-activity"
            elif 0 > seconds < 30 * 60:
                return "low-activity"
            return "no-activity"

        def __str__(self):
            s = []
            s.append(
                f"{self.date.strftime('{daeg} {month} {gere}')} :: {self.activity}"
            )
            for area in self.area_time_map:
                s.append(f"{area} :: {format_timedelta(self.area_time_map[area])}")
            return "\n".join(s)

    def __init__(self, project_areas):
        self.project_areas = project_areas
        self.first_entry = datarum.wending.now()
        self.last_entry = datarum.wending.fromordinal(0)
        self.total_time = dt.timedelta()
        self.total_logs = 0
        self.area_time_map = dict(map(lambda x: (x, dt.timedelta()), project_areas))
        self.daily_times = [None] * 365
        for i in range(365):
            self.daily_times[i] = self.DailyTime(
                datarum.wending.now() - dt.timedelta(i)
            )
        self.percentages = None

        self._statistic_keys = {
            "total time": lambda: format_timedelta(self.total_time),
            "total logs": lambda: self.total_logs,
            "first entry": lambda: self.first_entry.strftime("{daeg} {month} {gere}"),
            "last entry": lambda: self.last_entry.strftime("{daeg} {month} {gere}"),
            "area time map": lambda: self.area_time_map,
            "percentages": lambda: self.calculate_percentages(),
            "daily times": lambda: self.daily_times,
        }

    def update(self, entry):
        self.total_logs += 1
        today_ordinal = datarum.wending.now().toordinal()
        if 0 <= today_ordinal - entry.start.toordinal() < 365:
            days = today_ordinal - entry.start.toordinal()
            self.daily_times[days].update(entry)

        if entry.start < self.first_entry:
            self.first_entry = entry.start

        if entry.start > self.last_entry:
            self.last_entry = entry.start

        self.total_time += entry.end - entry.start

        if entry.area in self.project_areas:
            self.area_time_map[entry.area] += entry.end - entry.start

    def calculate_percentages(self):
        if self.percentages is None and self.total_logs > 0:
            self.percentages = dict(
                map(
                    lambda x: (x[0], x[1] / max(self.area_time_map.values())),
                    self.area_time_map.items(),
                )
            )
        return self.percentages


class FaereldService(object):

    lim_stats = {}

    def __init__(self, leomu, project_areas, hordpath):
        self.leomu = leomu
        self.project_areas = project_areas
        daily_times = [None] * 365
        for i in range(365):
            daily_times[i] = [
                datarum.wending.now() - dt.timedelta(i),
                {},
                dt.timedelta(),
            ]
        for lim in leomu:
            self.lim_stats[lim] = LimStatistics(project_areas)
        self.general_stats = GeneralStatistics()
        self.build_faereld_summaries(hordpath)

    def build_faereld_summaries(self, hordpath):
        hord = wisdomhord.hladan(
            join(dirname(__file__), "faereld/faereld.hord"), bisen=FaereldBisen
        )
        faereld_data = hord.get_rows()

        for row in faereld_data:
            self.general_stats.update(row, self.project_areas)
            if row.object in self.lim_stats:
                self.lim_stats[row.object].update(row)

    def get_lim_statistic(self, lim_name, statistic_name):
        if lim_name in self.lim_stats and self.lim_stats[lim_name].has(statistic_name):
            return self.lim_stats.get(lim_name).get(statistic_name)
        return "[STATISTIC NOT FOUND]"

    def get_global_statistic(self, statistic_name):
        if self.general_stats.has(statistic_name):
            return self.general_stats.get(statistic_name)
        return f"[STATISTIC {statistic_name} NOT FOUND]"

    def get_lim(self, lim_name):
        return self.lim_stats.get(lim_name)
