# -*- coding: utf-8 -*-
import yaml
from os.path import dirname, join
import bleach
import re
from flask import url_for, render_template

class Lim(object):

    def __init__(self, key, lim):
        self.key = key
        self.name = lim.get('name', "")
        self.brief = lim.get('brief', "")
        self.project = lim.get('project', False)
        self.head = lim.get('head', "")
        self.body = lim.get('body', "")
        self.externals = lim.get('externals', None)

    def to_html(self):
        return self._parse_body()

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


with open(join(dirname(__file__), "leomu/leomu.yml"), "r") as leomu_yml:
    leomu = yaml.load(leomu_yml)
    for key, value in leomu.items():
        leomu[key] = Lim(key, value)
