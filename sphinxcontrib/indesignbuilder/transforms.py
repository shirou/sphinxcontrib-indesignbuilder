# -*- coding: utf-8 -*-
from docutils import nodes
from sphinx.transforms import SphinxTransform
from sphinx.util import logging

logger = logging.getLogger(__name__)


class IdgxmlFootnoteTransform(SphinxTransform):
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


def setup(app):
    app.add_post_transform(IdgxmlFootnoteTransform)
