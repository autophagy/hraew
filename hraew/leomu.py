# -*- coding: utf-8 -*-
import yaml
from os.path import dirname, join
import bleach
import re
from flask import url_for

class Lim(object):

    def __init__(self, key, name, head, body):
        self.key = key
        self.name = name
        self.head = head
        self.body = body

    def to_html(self):
        return self._parse_body()

    def _parse_body(self):
        elements = self.body.split('\n\n')
        html_elements = []

        for element in elements:
            ele_head = self._get_element_head(element)

            if ele_head.strip() == '[BILIÞ]':
                html_elements.append(self._create_image(element))
            else:
                # Just treat it as a paragraph
                html_elements.append(self._create_paragraph(element))

        return '\n'.join(html_elements)

    def _get_element_head(self, element):
        element_lines = element.split('\n')
        return element_lines[0]

    def _create_paragraph(self, element):
        paragraph_wrap = "<p>{0}</p>"
        paragraph = paragraph_wrap.format(bleach.clean(element))
        return paragraph

    def _create_image(self, element):
        # Image tags will be in the form:
        # [BILIÞ]
        # [image.format :: optional caption]

        image_tag = "<div class='img-container'> <img src='{image_src}' alt='{image_alt}' /> </div>"
        image_loc = 'bilitha/leomu/{key}/{image_uri}'

        regex = '\[(.*?)\]'

        try:
            image_definition = element.split('\n')[1]
            image_definition = re.search(regex, image_definition).group(1)

            image_uri = ''
            image_alt = ''

            if '::' in image_definition:
                image_uri, image_alt = image_definition.split('::')
            else:
                image_uri = image_definition

            image_uri = url_for('static', filename=image_loc.format(key=self.key, image_uri=image_uri.strip()))

            return image_tag.format(image_src=image_uri, image_alt=image_alt.strip())
        except Exception as e:
            print(e)
            print("{0} is an invalid image definition.".format(image_definition))
            return ''


with open(join(dirname(__file__), "leomu/leomu.yml"), "r") as leomu_yml:
    leomu = yaml.load(leomu_yml)
    for key, value in leomu.items():
        leomu[key] = Lim(key, value['name'], value['head'], value['body'])
