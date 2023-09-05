# -*- coding: utf-8 -*-
from docutils import nodes
from sphinx import transforms
from sphinx.transforms import SphinxTransform
from sphinx.util import logging
from sphinx import addnodes

_logger = logging.getLogger(__file__)

class IdgxmlTransform(SphinxTransform):
    default_priority = 300

    def transform_indd_table(self):
        # type: () -> None
        ths = self.document.traverse(nodes.thead)
        if len(ths) == 0:
            return
        for th in ths:
            tb = th.parent.traverse(nodes.tbody)[0]
            tb.insert(0, th.children[0])
            th.parent.remove(th)

    def transform_footnote(self):
        # type: () -> None
        for fn_ref in self.document.traverse(nodes.footnote_reference):
            for fn in self.document.traverse(nodes.footnote):
                if fn['ids'][0] == fn_ref['refid']:
                    if fn_ref in fn_ref.parent.children:
                        fn_ref.parent.replace(fn_ref, fn.deepcopy())
                        fn['classes'].append('obsolated')

    def transform_fignumbers(self):
        # type: () -> None
        fignumbers = self.app.env.toc_fignumbers
        for docname in fignumbers.keys():
            for figtype in fignumbers[docname].keys():
                cnt = 1
                for fig in fignumbers[docname][figtype]:
                    fignum = fignumbers[docname][figtype][fig][0]
                    fignumbers[docname][figtype][fig] = (fignum, cnt)
                    cnt = cnt + 1

    def transform_chap_doc_footnote(self):
        # type: () -> None
        fns = self.document.traverse(nodes.footnote)
        fn_refs = self.document.traverse(nodes.footnote_reference)
        if 'docname' not in self.document.attributes:
            return
        for fn in fns:
            fn['ids'][0] = '{}-{}'.format(fn['docname'].split('/')[1], fn['ids'][0])
        for fn_ref in fn_refs:
            fn_ref['refid'] = '{}-{}'.format(fn_ref['docname'], fn_ref['refid'])

    def apply(self):
        # type: () -> None
        if 'indesign' not in self.app.builder.name:
            return

        if self.app.builder.name == 'chapteredindesign':
            self.transform_chap_doc_footnote()

        self.transform_indd_table()
        self.transform_footnote()
        self.transform_fignumbers()

def setup(app):
    # type: () -> None
    app.add_post_transform(IdgxmlTransform)
