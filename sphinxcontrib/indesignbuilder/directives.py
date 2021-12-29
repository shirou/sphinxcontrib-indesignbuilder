# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

from docutils.parsers.rst.directives.admonitions import Admonition
from docutils import nodes


class note(nodes.admonition):
    pass


class NamedNoteDirective(Admonition):
    node_class = note
    css_class = 'note'
    required_arguments = 0
    optional_arguments = 1

    def run(self):
        title = u''
        if self.arguments:
            title += self.arguments[0]

        if 'class' in self.options:
            self.options['class'].append(self.css_class)
        else:
            self.options['class'] = [self.css_class]

        ret = Admonition.run(self)
        ret[0]['title'] = title
        ret[0]['name'] = self.name
        return ret

