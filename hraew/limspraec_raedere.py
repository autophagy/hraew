import re


class LimspræcRædere(object):
    def raed(self, path):
        leomu = {}
        current_lim = None
        current_attributes = {}
        current_attribute = None
        current_indent = 0

        with open(path, "r") as leomu_definition:
            for line in leomu_definition.readlines():
                cleansed_line = line.rstrip("\n")
                tag = self.lim_tag(cleansed_line)
                if tag:
                    if current_lim is not None:
                        leomu[current_lim] = current_attributes
                    current_lim = tag
                    current_attributes = {}
                else:
                    if self.is_attribute(line):
                        attr, content = line.split(" :: ", 1)
                        if self.is_attribute(content.strip()):
                            current_attribute = attr.strip()
                            sub_attr, sub_content = content.strip().split(" :: ", 1)
                            current_attributes[current_attribute] = {
                                sub_attr.strip(): sub_content.strip()
                            }
                        else:
                            current_attribute = attr.strip()
                            current_attributes[current_attribute] = content.strip()
                        current_indent = len(attr) + 1
                    else:
                        if self.is_part_of_same_line(line, current_indent):
                            content = current_attributes[current_attribute]
                            if line[current_indent:].strip() == '::':
                                subline = '\n'
                            else:
                                subline = line[current_indent:].strip().split('::', 1)[1]
                            if isinstance(content, dict) and self.is_attribute(subline):
                                sub_attr, sub_content = subline.strip().split(" :: ", 1)
                                current_attributes[current_attribute][
                                    sub_attr.strip()
                                ] = sub_content
                            else:
                                current_attributes[current_attribute] = "\n".join(
                                    [content, subline.strip()]
                                )
        leomu[current_lim] = current_attributes
        return leomu

    def lim_tag(self, line):
        match = re.match(r"^\[(.+)\]$", line)
        if match:
            return match.group(1).strip()

    def is_attribute(self, line):
        return re.match(r"^[a-zA-Z0-9_\- ]+ +:: .+$", line.strip()) is not None

    def is_part_of_same_line(self, line, indent):
        return re.match(r"^ {" + str(indent) + r"}::", line) is not None
