# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

from six import iteritems
import os
from os import path

from docutils import nodes
from sphinx.builders import Builder
from sphinx.util import logging
from sphinx.util.console import bold, darkgreen, brown
from sphinx.util.nodes import inline_all_toctrees
from sphinx.util.osutil import ensuredir, copyfile

from sphinxcontrib.indesignbuilder.writer import IndesignWriter
from sphinxcontrib.indesignbuilder.webdbwriter import WebDBXMLWriter

logger = logging.getLogger(__file__)


class IndesignXMLBuilder(Builder):
    """
    Builds indesign xml.
    """
    name = 'indesign'
    format = 'xml'
    out_suffix = '.xml'
    supported_image_types = ['image/svg+xml', 'image/png',
                             'image/gif', 'image/jpeg']

    def get_outdated_docs(self):
        return []

    def fix_refuris(self, tree):
        # fix refuris with double anchor
        fname = self.config.master_doc + self.out_suffix
        for refnode in tree.traverse(nodes.reference):
            if 'refuri' not in refnode:
                continue
            refuri = refnode['refuri']
            hashindex = refuri.find('#')
            if hashindex < 0:
                continue
            hashindex = refuri.find('#', hashindex+1)
            if hashindex >= 0:
                refnode['refuri'] = fname + refuri[hashindex:]

    def prepare_writing(self, docnames, single=False):
        if single:
            self.docwriter = IndesignWriter(self, single=True)
        else:
            self.docwriter = IndesignWriter(self)
        if not path.exists(self.outdir):
            os.makedirs(self.outdir)
        self._docnames = docnames

    def write_doc(self, docname, doctree):
        self.fignumbers = self.env.toc_fignumbers.get(docname, {})
        if docname.find("/") >= 0:
            ensuredir(os.path.join(self.outdir, docname.split("/")[0]))
        with open(os.path.join(self.outdir,
                               docname + ".xml"), "w", encoding="utf-8") as f:
            self.docwriter.write(doctree, f)

    def get_target_uri(self, docname, typ=None):
        return docname + self.out_suffix

    def copy_image_files(self):
        # copy image files
        if self.images:
            ensuredir(os.path.join(self.outdir, self.imagedir))
            for src in self.app.status_iterator(self.images,
                                                'copying images... ',
                                                brown, len(self.images)):
                dest = self.images[src]
                try:
                    copyfile(path.join(self.srcdir, src),
                             path.join(self.outdir, self.imagedir, dest))
                except Exception as err:
                    logger.warn('cannot copy image file %r: %s' %(
                        path.join(self.srcdir, src), err))

    def copy_download_files(self):
        # copy downloadable files
        if self.env.dlfiles:
            ensuredir(path.join(self.outdir, '_downloads'))
            for src in self.app.status_iterator(
                    self.env.dlfiles,
                    'copying downloadable files... ',
                    brown, len(self.env.dlfiles)):
                dest = self.env.dlfiles[src][1]
                try:
                    copyfile(path.join(self.srcdir, src),
                             path.join(self.outdir, '_downloads', dest))
                except Exception as err:
                    logger.warn('cannot copy downloadable file %r: %s' %
                              (path.join(self.srcdir, src), err))


class SingleIndesignXMLBuilder(IndesignXMLBuilder):
    """
    A SingleIndesignXMLBuilder subclass that puts the whole document tree
    on one Indesign XML file.
    """
    name = 'singleindesign'
    copysource = False
    out_suffix = '.xml'

    def get_outdated_docs(self):
        return 'all documents'

    def get_target_uri(self, docname, typ=None):
        if docname in self.env.all_docs:
            # all references are on the same page...
            return self.config.master_doc + self.out_suffix + \
                '#document-' + docname
        else:
            # chances are this is a html_additional_page
            return docname + self.out_suffix

    def get_relative_uri(self, from_, to, typ=None):
        # ignore source
        return self.get_target_uri(to, typ)

    def assemble_doctree(self):
        master = self.config.master_doc
        tree = self.env.get_doctree(master)
        tree = inline_all_toctrees(
            self, set(), master, tree, darkgreen, [master])
        tree['docname'] = master
        self.env.resolve_references(tree, master, self)
        return tree

    def assemble_toc_secnumbers(self):
        # Assemble toc_secnumbers to resolve section numbers on SingleHTML.
        # Merge all secnumbers to single secnumber.
        #
        # Note: current Sphinx has refid confliction in singlehtml mode.
        #       To avoid the problem, it replaces key of secnumbers to
        #       tuple of docname and refid.
        #
        #       There are related codes in inline_all_toctres() and
        #       HTMLTranslter#add_secnumber().
        new_secnumbers = {}
        for docname, secnums in iteritems(self.env.toc_secnumbers):
            for id, secnum in iteritems(secnums):
                new_secnumbers[(docname, id)] = secnum

        return {self.config.master_doc: new_secnumbers}

    def get_doc_context(self, docname, body, metatags):
        # no relation links...
        toc = self.env.get_toctree_for(self.config.master_doc, self, False)
        # if there is no toctree, toc is None
        if toc:
            self.fix_refuris(toc)
            toc = self.render_partial(toc)['fragment']
            display_toc = True
        else:
            toc = ''
            display_toc = False
        return dict(
            parents=[],
            prev=None,
            next=None,
            docstitle=None,
            title=self.config.html_title,
            meta=None,
            body=body,
            metatags=metatags,
            rellinks=[],
            sourcename='',
            toc=toc,
            display_toc=display_toc,
        )

    def write(self, *ignored):
        docnames = self.env.all_docs

        logger.info(bold('preparing documents... '), nonl=True)
        self.prepare_writing(docnames, single=True)
        logger.info('done')

        logger.info(bold('assembling single document... '), nonl=True)
        doctree = self.assemble_doctree()
        self.env.toc_secnumbers = self.assemble_toc_secnumbers()
        logger.info(bold('writing... '), nonl=True)
        self.write_doc_serialized(self.config.master_doc, doctree)
        self.write_doc(self.config.master_doc, doctree)
        logger.info('done')

    def finish(self):
        self.copy_image_files()
        self.copy_download_files()


class ChapteredIndesignXMLBuilder(SingleIndesignXMLBuilder):
    """
    A SingleIndesignXMLBuilder subclass that puts document tree
    into Re:VIEW styled Indesign XML file by chapter.
    """
    name = 'chapteredindesign'
    copysource = False
    out_suffix = '.xml'

    def assemble_doctree(self, chap):
        master = '{}/{}'.format(chap, self.config.master_doc)
        try:
            tree = self.env.get_doctree(master)
        except FileNotFoundError:
            logger.warn('{} not found...'.format(master))
            return None
        tree = inline_all_toctrees(
            self, set(), master, tree, darkgreen, [master])
        tree['docname'] = master
        self.env.resolve_references(tree, master, self)
        self.fix_refuris(tree)
        return tree

    def write(self, *ignored):
        all_docs = self.env.all_docs
        self.fignumbers = self.env.toc_fignumbers.get(docname, {})
        chaps = list(set([doc.split('/')[0] for doc in all_docs.keys()]))
        for chap in chaps:
            if chap != 'index':
                docnames = dict(
                    [doc for doc in all_docs.items()
                        if doc[0].startswith(chap)])
                logger.info(bold('preparing documents... '), nonl=True)
                self.prepare_writing(docnames, single=True)
                logger.info('done')

                logger.info(bold('assembling chapter document... '), nonl=True)
                doctree = self.assemble_doctree(chap)
                if doctree is not None:
                    self.env.toc_secnumbers = self.assemble_toc_secnumbers()
                    logger.info(bold('writing... '), nonl=True)
                    master_doc = '{}/{}'.format(chap, self.config.master_doc)
                    self.write_doc_serialized(master_doc, doctree)
                    self.write_doc(master_doc, doctree)
                    logger.info('done')
                else:
                    logger.info('writing ignored... continue')


class WebDBXMLBuilder(IndesignXMLBuilder):
    name = 'webdb'
    out_suffix = '.xml'

    def prepare_writing(self, docnames, single=False):
        self.docwriter = WebDBXMLWriter(self, single=False)
        if not path.exists(self.outdir):
            os.makedirs(self.outdir)
        self._docnames = docnames


class SingleWebDBXMLBuilder(SingleIndesignXMLBuilder):
    name = 'singlewebdb'
    out_suffix = '.xml'

    def prepare_writing(self, docnames, single=False):
        self.docwriter = WebDBXMLWriter(self, single=True)
        if not path.exists(self.outdir):
            os.makedirs(self.outdir)
        self._docnames = docnames


def setup(app):
    app.add_builder(IndesignXMLBuilder)
    app.add_builder(SingleIndesignXMLBuilder)
    app.add_builder(WebDBXMLBuilder)
    app.add_builder(SingleWebDBXMLBuilder)
    app.add_builder(ChapteredIndesignXMLBuilder)

    # :indesign_builder_numfig_puncutuate_mark:
    #       numfigに挿入する章番号と図番号の接続記号を指定する。
    app.add_config_value('indesign_builder_numfig_puncutuate_mark', '.', 'env')