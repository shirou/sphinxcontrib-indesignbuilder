# -*- coding: utf-8 -*-
from docutils import nodes
from sphinx import transforms
from sphinx.transforms import SphinxTransform
from sphinx.util import logging


class IdgxmlFootnoteTransform(SphinxTransform):
    default_priority = 300

    def transform_indd_table(self):
        ths = self.document.traverse(nodes.thead)
        if len(ths) == 0:
            return
        for th in ths:
            tb = th.parent.traverse(nodes.tbody)[0]
            tb.insert(0, th.children[0])
            th.parent.remove(th)

    def transform_chaptered_doc(self):
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
            self.transform_chaptered_doc()

        fns = self.document.traverse(nodes.footnote)
        fn_refs = self.document.traverse(nodes.footnote_reference)

        self.transform_indd_table()

        for fn_ref in fn_refs:
            for fn in fns:
                if fn['ids'][0] in fn_ref['refid']:
                    if fn_ref in fn_ref.parent.children:
                        fn_ref.parent.replace(old=fn_ref, new=fn.deepcopy())
                        fn['classes'].append('obsolated')


def setup(app):
    app.add_post_transform(IdgxmlFootnoteTransform)
