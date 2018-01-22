# -*- coding: utf-8 -*-
import yaml
from os.path import dirname, join

class Lim(object):

    def __init__(self, name, head, body):
        self.name = name
        self.head = head
        self.body = body

    def to_html(self):
        return parse_body(self.body)

def parse_body(lim_body):
    paragraph_wrap = "<p>{0}</p>"
    paragraphs = list(map(lambda x: x.replace('\n', ''), lim_body.split('\n\n')))

    wrapped_paragraphs = list(map(lambda x: paragraph_wrap.format(x), paragraphs))
    return '\n'.join(wrapped_paragraphs)


with open(join(dirname(__file__), "leomu/leomu.yml"), "r") as leomu_yml:
    leomu = yaml.load(leomu_yml)
    for key, value in leomu.items():
        leomu[key] = Lim(value['name'], value['head'], value['body'])
