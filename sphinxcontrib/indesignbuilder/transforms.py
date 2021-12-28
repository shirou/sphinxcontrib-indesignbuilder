# -*- coding: utf-8 -*-
"""
    sphinxcontrib-indesignbuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2015-2018 by the WAKAYAMA Shirou, Akihiro Takizawa
    :license: BSD, see LICENSE for details.

"""

import re

from docutils import nodes
from docutils.nodes import Text, subscript, superscript
from sphinx import addnodes
from sphinx.locale import __
from sphinx.transforms import SphinxTransform
from sphinx.util import logging

from math_symbols import math_equation_symbols

SUPER_OR_SUB = re.compile('[_^]\\{[^}]+\\}')

logger = logging.getLogger(__name__)


class IdgxmlTransform(SphinxTransform):
    default_priority = 100

    def apply(self):
        # type: () -> None
        if self.app.builder.name != 'indesign':
            return
        # TBD: footnote and footnote_ref can't work expected.
        #      autofootnote is going well.
        for fn_ref in self.document.footnote_refs:
            for fn in self.document.footnotes:
                if fn_ref == fn['names'][0]:
                    fn.remove(fn.children[0])
                    self.document.footnote_refs[fn_ref][0] = fn.deepcopy()
                    break
        for autofn_ref in self.document.autofootnote_refs:
            cur_id = autofn_ref['refid']
            for autofn in self.document.autofootnotes:
                if autofn['ids'][0] == cur_id:
                    autofn.remove(autofn.children[0])
                    cur_fn = autofn.deepcopy()
                    autofn_ref.replace_self(cur_fn)
                    autofn.parent.remove(autofn)
                    break
        # compact list item having nested bullet list.
        for node in self.document.traverse(nodes.bullet_list):
            for list_item in node.children:
                if isinstance(list_item.children[0], nodes.definition_list):
                    nested_item = nodes.list_item()
                    def_list = list_item.children[0]
                    for sub_item in def_list:
                        sub_para = nodes.paragraph()
                        sub_para.append(sub_item[0][0])
                        nested_item.append(sub_para)
                        nested_item.append(sub_item[1][0].deepcopy())
                    list_item.replace_self(nested_item)

        for node in self.document.traverse(addnodes.nodes.math_block):
            math_source = self.replace_math_symbol(node.astext())
            if math_source.find('\\') == -1:
                node.children = self.text_to_super_or_subscript(math_source)
            else:
                pass
        for node in self.document.traverse(addnodes.nodes.math):
            math_source = self.replace_math_symbol(node.astext())
            if math_source.find('\\') == -1:
                node.children = self.text_to_super_or_subscript(math_source)
            else:
                pass

    def replace_math_symbol(self, source):
        # type: (str) -> str
        logger.warning(__('replace TeX equation symbols.'))
        for name in math_equation_symbols.keys():
            symbol = chr(math_equation_symbols[name])
            source = source.replace(f'\\{name}', symbol)
        return source

    def text_to_super_or_subscript(self, source):
        # type: (str) -> list
        items = SUPER_OR_SUB.split(source)
        subitems = SUPER_OR_SUB.findall(source)
        buf = []
        pos = 0
        for item in items:
            if item == '':
                if subitems[pos].startswith('^'):
                    buf.append(
                        superscript(
                            text=subitems[pos].replace(
                                '^{', '').replace('}', '')))
                elif subitems[pos].startswith('_'):
                    buf.append(
                        subscript(
                            text=subitems[pos].replace(
                                '_{', '').replace('}', '')))
                pos = pos + 1
            else:
                buf.append(Text(item))
        return buf


def setup(app):
    app.add_post_transform(IdgxmlTransform)
