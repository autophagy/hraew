# -*- coding: utf-8 -*-
from docutils.core import publish_parts
import yaml
from os.path import dirname, join

class Entry(object):

    def __init__(self, name, head, body):
        self.name = name
        self.head = head
        self.body = body

    def to_html(self):
        return publish_parts(self.body, writer_name="html")["html_body"]

with open(join(dirname(__file__), "entries.yml"), "r") as entries_yml:
    entries = yaml.load(entries_yml)
    for key, value in entries.items():
        entries[key] = Entry(value['name'], value['head'], value['body'])
