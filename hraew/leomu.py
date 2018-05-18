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

class Lim(object):

    _body_html = None

    def __init__(self, key, lim):
        self.key = key
        self.name = lim.get('name', "")
        self.brief = lim.get('brief', "")
        self.project = lim.get('project', False)
        self.status = lim.get('status', "n/a")
        self.head = lim.get('head', "")
        self.body = lim.get('body', "")
        self.foot = lim.get('foot', "")
        self.externals = lim.get('externals', None)

    def to_html(self):
        if self._body_html is None:
            self._body_html = self._parse_body()

        return self._body_html

    def _parse_body(self):
        elements = self.body.split('\n\n')
        html_elements = []

        gewissung_mode = False
        gewissung_block = None

        for element in elements:
            ele_head = self._get_element_head(element)

            if gewissung_mode:
                ele_foot = self._get_element_foot(element)
                if ele_foot.strip() == '[GEWISSUNGENDE]':
                    gewissung_block = "{0}\n\n{1}".format(gewissung_block, element.replace(ele_foot, ''))
                    html_elements.append(self._create_gewissung(gewissung_block))
                    gewissung_mode = False
                    gewissung_block = None
                else:
                    gewissung_block = "{0}\n\n{1}".format(gewissung_block, element)
            else:
                if ele_head.strip() == '[BILIÞ]':
                    html_elements.append(self._create_image(element))
                elif ele_head.strip() == '[CUNNUNGARC]':
                    html_elements.append(self._create_cunnungarc(element))
                elif ele_head.strip() == '[GEWISSUNG]':
                    gewissung_mode = True
                    gewissung_block = element.replace("{}\n".format(ele_head), '')
                else:
                    # Just treat it as a paragraph
                    html_elements.append(self._create_paragraph(element))

        return '\n'.join(html_elements)

    def _get_element_head(self, element):
        element_lines = element.strip().split('\n')
        return element_lines[0]

    def _get_element_foot(self, element):
        element_lines = element.strip().split('\n')
        return element_lines[-1]

    def _create_paragraph(self, element):
        paragraph_wrap = "<p>{0}</p>"
        element = bleach.clean(element)

        # Parse geþeodan
        geþeodanified_element = self._create_geþeodan(element)

        paragraph = paragraph_wrap.format(geþeodanified_element)
        return paragraph

    def _create_image(self, element):
        # Image tags will be in the form:
        # [BILIÞ]
        # [image.format :: optional caption]

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

            return render_template('bilith.html', lim_key=self.key,
                                                  image_uri=image_uri.strip(),
                                                  image_alt=image_alt.strip())
        except Exception:
            print("{0} is an invalid image definition.".format(image_definition))
            return ''

    def _create_geþeodan(self, element):
        # Geþeodan tags will be in the form
        # [GEÞEODAN :: uri :: geþeodan]

        def get_geþeodan_elements(geþeodan_string):
            try:
                if '::' in geþeodan_string:
                    geþeodan_uri, geþeodan_text = geþeodan_string.split('::')
                else:
                    geþeodan_uri = geþeodan_string
                    geþeodan_text = geþeodan_string
                return {'uri': geþeodan_uri.strip(),
                        'text': geþeodan_text.strip()}
            except Exception:
                print("{0} is an invalid getheodan definition.".format(geþeodan_string))

        regex = re.compile('\[GEÞEODAN :: (.*?)\]')

        # Create innan geþeodan
        element = regex.sub(lambda x: render_template('getheodan.html',
                            geþeodan=get_geþeodan_elements(x.group(1))), element)

        return element

    def _create_cunnungarc(self, element):
        # Cunnungarc tags in the form:
        # [CUNNUNGARC]
        # [ HEADER1 | HEADER2 | HEADER3 ]
        # [ row1    | row2    | row3    ]

        def create_element_list(cunnungarc_string):
            try:
                regex = '\[(.*?)\]'

                element_list = re.match(regex, cunnungarc_string).group(1).split('|')
                return list(map(lambda x: bleach.clean(x.strip()), element_list))
            except Exception:
                print("{0} is an invalid cunnungarc row definition.".format(cunnungarc_string))

        try:
            # Discard the header tag
            cunnungarc_rows = element.split('\n')
            cunnungarc_rows.pop(0)

            cunnungarc_rows = list(filter(lambda x: x != '', cunnungarc_rows))
            cunnungarc_head = cunnungarc_rows.pop(0)
            headers = create_element_list(cunnungarc_head)
            rows = list(map(lambda x: create_element_list(x), cunnungarc_rows))

            return render_template('cunnungarc.html', headers=headers, rows=rows)
        except Exception:
            print(cunnungarc_string)
            print("is an invalid cunnungarc definition.")
            return ''

    def _create_gewissung(self, gewissung_block):
        return render_template('gewissung.html', gewissung=gewissung_block)


class FaereldLim(object):

    PROJECT_AREAS = ['RES', 'DES', 'DEV', 'DOC', 'TST']

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
            start = row['START']
            end = row['END']

            if first_entry is None:
                first_entry = start
            if last_entry is None:
                last_entry = end

            if start < first_entry:
                first_entry = start

            if start > last_entry:
                last_entry = start

            self.total_time += end - start

            if area_time_map.get(row['AREA']) is None:
                area_time_map[row['AREA']] = end - start
            else:
                area_time_map[row['AREA']] += end - start

        self.percentages = dict(map(lambda x: (x[0], x[1]/max(area_time_map.values())),
                                    area_time_map.items()))
        self.first_entry = first_entry.strftime('{daeg} {month} {gere}')
        self.last_entry = last_entry.strftime('{daeg} {month} {gere}')


    def formatted_total_time(self):
        hours, remainder = divmod(self.total_time.total_seconds(), 3600)
        minutes = floor(remainder/60)

        return "{0}h{1}m".format(floor(hours), minutes)

class FaereldBisen(Bisen):

    __invoker__ = 'Færeld'
    __description__ = 'Productive task time tracking data produced by Færeld'

    col1 = Sweor('AREA',   wisdomhord.String)
    col2 = Sweor('OBJECT', wisdomhord.String)
    col3 = Sweor('START',  wisdomhord.Wending)
    col4 = Sweor('END',    wisdomhord.Wending)


def get_projects_faereld_data(faereld_rows):
    faereld_data = {}
    faereld_leomu = {}

    for row in faereld_rows:
        if faereld_data.get(row['OBJECT']) is None:
            faereld_data[row['OBJECT']] = [row]
        else:
            faereld_data[row['OBJECT']].append(row)

    for k,v in faereld_data.items():
        faereld_leomu[k] = FaereldLim(v)

    return faereld_leomu


with open(join(dirname(__file__), "leomu/leomu.yml"), "r") as leomu_yml:
    leomu = yaml.load(leomu_yml)
    for key, value in leomu.items():
        leomu[key] = Lim(key, value)

hord = wisdomhord.hladan(join(dirname(__file__), "faereld/faereld.hord"), bisen=FaereldBisen)

project_areas = ['RES', 'DES', 'DEV', 'DOC', 'TST']

faereld_data = get_projects_faereld_data(hord.get_rows(filter_func=lambda x: x['AREA'] in project_areas and x['OBJECT'] in leomu.keys()))
