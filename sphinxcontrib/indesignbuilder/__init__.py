# -*- coding: utf-8 -*-
"""
    sphinxcontrib-indesignbuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2015 by the WAKAYAMA Shirou
    :license: BSD, see LICENSE for details.
"""

from __future__ import absolute_import

from docutils import nodes

from sphinxcontrib.indesignbuilder import indesignbuilder, transforms


# from japanesesupport.py
def trunc_whitespace(app, doctree, docname):
    for node in doctree.traverse(nodes.Text):
        if isinstance(node.parent, nodes.paragraph) and \
                (not node.astext().isspace()):
            newtext = node.astext()
            for c in "\n\r\t":
                newtext = newtext.replace(c, "")
            newtext = newtext.strip()
            node.parent.replace(node, nodes.Text(newtext))


def setup(app):
    app.connect("doctree-resolved", trunc_whitespace)
    indesignbuilder.setup(app)
    transforms.setup(app)
