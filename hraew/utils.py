from math import floor

def format_timedelta(delta):
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes = floor(remainder / 60)
        return "{0}h{1}m".format(floor(hours), minutes)
