# -*- coding: utf-8 -*-
import yaml
from os.path import dirname, join

class Tramet(object):

    def __init__(self, name, head, body):
        self.name = name
        self.head = head
        self.body = body

    def to_html(self):
        return parse_body(self.body)

def parse_body(tramet_body):
    paragraph_wrap = "<p>{0}</p>"
    paragraphs = list(map(lambda x: x.replace('\n', ''), tramet_body.split('\n\n')))

    wrapped_paragraphs = list(map(lambda x: paragraph_wrap.format(x), paragraphs))
    return '\n'.join(wrapped_paragraphs)


with open(join(dirname(__file__), "trametas/trametas.yml"), "r") as trametas_yml:
    trametas = yaml.load(trametas_yml)
    for key, value in trametas.items():
        trametas[key] = Tramet(value['name'], value['head'], value['body'])
