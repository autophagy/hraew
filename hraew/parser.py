from abc import ABC, abstractmethod
from flask import render_template
import re
import bleach


class Element(ABC):

    template_options = {}

    def __init__(self, key, text):
        self.key = key
        self.text = text
        super().__init__()

    @property
    @abstractmethod
    def html_template(self):
        pass

    def render_html(self):
        return render_template(self.html_template, **self.template_options)

    @abstractmethod
    def parse(self):
        pass


class HeadElement(Element):

    @property
    @abstractmethod
    def head(self):
        pass


class BlockElement(HeadElement):

    def __init__(self, key, text):
        self.elements = []
        self.elements.append(text)
        super().__init__(key, text)

    @property
    @abstractmethod
    def foot(self):
        pass

    def add_element(self, text):
        self.elements.append(text)

    def strip_tags(self):
        self.elements[0] = self.elements[0].replace(self.head + "\n", "", 1)
        self.elements[-1] = "".join(self.elements[-1].rsplit("\n" + self.foot, 1))


class Geþeodan(Element):

    html_template = "getheodan.html"

    def parse(self):
        regex = re.compile("\[GEÞEODAN :: (.*?)\]")
        geþeodan_string = re.search(regex, self.text.strip()).group(1)

        if "::" in geþeodan_string:
            geþeodan_uri, geþeodan_text = geþeodan_string.split("::")
        else:
            geþeodan_uri = geþeodan_string
            geþeodan_text = geþeodan_string

        self.template_options = {
            "uri": geþeodan_uri.strip(),
            "text": geþeodan_text.strip(),
        }


class Biliþ(HeadElement):

    html_template = "bilith.html"
    head = "[BILIÞ]"

    def parse(self):
        regex = "\[(.*?)\]"

        image_definition = self.text.split("\n")[1]
        image_definition = re.search(regex, image_definition).group(1)

        image_uri = ""
        image_alt = ""

        if "::" in image_definition:
            image_uri, image_alt = image_definition.split("::")
        else:
            image_uri = image_definition

        self.template_options = {
            "lim_key": self.key,
            "image_uri": image_uri.strip(),
            "image_alt": image_alt.strip(),
        }


class Cunnungarc(HeadElement):

    html_template = "cunnungarc.html"
    head = "[CUNNUNGARC]"

    def parse(self):

        def create_element_list(cunnungarc_string):
            regex = "\[(.*?)\]"

            element_list = (
                re.match(regex, cunnungarc_string.strip()).group(1).split("|")
            )
            return list(map(lambda x: bleach.clean(x.strip()), element_list))

        # Discard the header tag
        cunnungarc_rows = self.text.split("\n")
        cunnungarc_rows.pop(0)

        cunnungarc_rows = list(filter(lambda x: x != "", cunnungarc_rows))
        cunnungarc_head = cunnungarc_rows.pop(0)
        headers = create_element_list(cunnungarc_head)
        rows = list(map(lambda x: create_element_list(x), cunnungarc_rows))

        self.template_options = {"headers": headers, "rows": rows}


class Gewissung(BlockElement):

    html_template = "gewissung.html"
    head = "[GEWISSUNG]"
    foot = "[GEWISSUNGENDE]"

    def parse(self):
        self.strip_tags()
        self.template_options = {"elements": self.elements}


class Paragraph(Element):

    html_template = "paragraph.html"

    def parse(self):
        element = bleach.clean(self.text)
        regex = re.compile("(\[GEÞEODAN :: .*?\])")

        paragraph_elements = re.split(regex, element)
        paragraph = []
        for paragraph_element in paragraph_elements:
            if re.match(regex, paragraph_element):
                geþeodan = Geþeodan(self.key, paragraph_element)
                geþeodan.parse()
                paragraph.append(geþeodan)
            else:
                paragraph.append(paragraph_element)

        self.template_options = {"paragraph": paragraph}

    def render_html(self):
        rendered_paragraph = ""
        for paragraph_element in self.template_options["paragraph"]:
            if isinstance(paragraph_element, Element):
                rendered_paragraph += paragraph_element.render_html()
            else:
                rendered_paragraph += paragraph_element
        self.template_options["paragraph"] = rendered_paragraph
        return super().render_html()


class Parser(object):

    def __init__(self, key, text):
        self.key = key
        self.text = text

    def parse(self):
        elements = self.text.split("\n\n")
        parsed_elements = []

        gewissung_mode = False
        gewissung_block = None

        for element in elements:
            ele_head = self._get_element_head(element)

            if gewissung_mode:
                ele_foot = self._get_element_foot(element)
                if ele_foot.strip() == Gewissung.foot:
                    gewissung_block = "{0}\n\n{1}".format(
                        gewissung_block, element.replace(ele_foot, "")
                    )
                    gewissung = Gewissung(self.key, gewissung_block)
                    gewissung.parse()
                    parsed_elements.append(gewissung)
                    gewissung_mode = False
                    gewissung_block = None
                else:
                    gewissung_block = "{0}\n\n{1}".format(gewissung_block, element)
            else:
                if ele_head.strip() == Biliþ.head:
                    biliþ = Biliþ(self.key, element)
                    biliþ.parse()
                    parsed_elements.append(biliþ)
                elif ele_head.strip() == Cunnungarc.head:
                    cunnungarc = Cunnungarc(self.key, element)
                    cunnungarc.parse()
                    parsed_elements.append(cunnungarc)
                elif ele_head.strip() == Gewissung.head:
                    gewissung_mode = True
                    gewissung_block = element.replace("{}\n".format(ele_head), "")
                else:
                    paragraph = Paragraph(self.key, element)
                    paragraph.parse()
                    parsed_elements.append(paragraph)

        return parsed_elements

    def render_html(self):
        html_elements = []
        parsed_elements = self.parse()
        for element in parsed_elements:
            html_elements.append(element.render_html())
        return "\n\n".join(html_elements)

    def _get_element_head(self, element):
        element_lines = element.strip().split("\n")
        return element_lines[0]

    def _get_element_foot(self, element):
        element_lines = element.strip().split("\n")
        return element_lines[-1]
