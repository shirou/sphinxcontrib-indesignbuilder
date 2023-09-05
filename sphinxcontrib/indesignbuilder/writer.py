# -*- coding: utf-8 -*-

import os

from docutils import nodes
from docutils.nodes import Element, NodeVisitor
from docutils.writers import Writer
from six import StringIO
from sphinx.util import logging
from xml.sax.saxutils import XMLGenerator

logger = logging.getLogger(__name__)

import os

class IndesignWriter(Writer):
    def __init__(self, builder, single=False):
        Writer.__init__(self)
        self.single = single
        self.builder = builder

    def translate(self):
        if self.single:
            self.visitor = visitor = SingleIndesignVisitor(self.document)
        else:
            self.visitor = visitor = IndesignVisitor(self.document, self.builder)
        self.document.walkabout(visitor)
        self.output = visitor.astext()


class IndesignVisitor(NodeVisitor):
    def __init__(self, document, builder):
        NodeVisitor.__init__(self, document)

        self.builder = builder
        self._output = StringIO()
        self.generator = XMLGenerator(self._output, "utf-8")
        self.generator.outf = self._output

        self.listenv = None
        self.listlevel = 0
        self.adomonienv = None
        self.tableenv = False
        self.within_index = False
        self.restrect_newline = True

    def newline(self):
        if self.restrect_newline is not True:
            self.generator.outf.write("\n")

    def astext(self):
        return self._output.getvalue()

    def add_fignumber(self, node: Element) -> None:
        def append_fignumber(figtype: str, figure_id: str) -> None:
            key = figtype
            if figure_id in self.builder.fignumbers.get(key, {}):
                self.generator.outf.write('<span class="caption-number">')
                prefix = self.builder.config.numfig_format.get(figtype)
                if prefix is None:
                    msg = __('numfig_format is not defined for %s') % figtype
                    logger.warning(msg)
                else:
                    numbers = self.builder.fignumbers[key][figure_id]
                    self.generator.outf.write(prefix % '-'.join(map(str, numbers)) + '：')
                    self.generator.outf.write('</span>')
        figtype = self.builder.env.domains['std'].get_enumerable_node_type(node)
        if figtype:
            if len(node['ids']) == 0:
                msg = __('Any IDs not assigned for %s node') % node.tagname
                logger.warning(msg, location=node)
            else:
                append_fignumber(figtype, node['ids'][0])


    def visit_document(self, node):
        self.generator.startDocument()

        self.generator.outf.write(
            '<doc xmlns:aid="http://ns.adobe.com/AdobeInDesign/4.0/">')
        self.sec_level = 0

    def depart_document(self, node):
        self.generator.endDocument()
        self.generator.outf.write("</doc>")

    def visit_paragraph(self, node):
        # does not print <p> in list
        if not (self.listenv or self.tableenv):
            self.generator.startElement('p', {})

    def depart_paragraph(self, node):
        if not (self.listenv or self.tableenv):
            self.generator.endElement('p')
            self.newline()

    def visit_section(self, node):
        assert not self.within_index
        self.sec_level += 1
        if node.previous_sibling().tagname != 'target':
            target_id = node['ids'][0]
            try:
                target_name = node['names'][0]
            except IndexError:
                target_name = node['dupnames'][0]
            self.generator.startElement(
                'a', {
                        'id': "#%s" % target_id,
                        'name': '%s' % target_name
                    }
                )
            self.generator.endElement('a')

    def depart_section(self, node):
        self.sec_level -= 1
        self.newline()

    def visit_title(self, node):
        level = "h" + str(self.sec_level)
        if 'refuri' in node:
            attrs = {"aid:pstyle": level, "refid": " ".join(node['refuri'])}
        else:
            attrs = {"aid:pstyle": level}
        self.generator.startElement('title', attrs)

    def depart_title(self, node):
        self.generator.endElement('title')
        dtp = u'<?dtp level="{0}" section="{1}"?>'.format(
            self.sec_level,
            node.astext(),
        )
        self.generator.outf.write(dtp)

        self.newline()

    def visit_Text(self, node):
        self.generator.characters(node.astext())

    def depart_Text(self, node):
        pass

    def visit_index(self, node):
        # self.generator.startElement('index', {})
        self.within_index = True
        pass

    def depart_index(self, node):
        # self.generator.endElement('index')
        self.within_index = False
        pass

    def visit_target(self, node):
        if len(node.attributes['ids']) > 0:
            atts = {'id': node['ids'][0]}
        elif node.attributes['refid']:
            atts = {'id': node['refid']}
        else:
            atts = {}
        self.generator.startElement('a', atts)

    def depart_target(self, node):
        self.generator.endElement('a')

    def visit_emphasis(self, node):
        self.generator.startElement("i", {})

    def depart_emphasis(self, node):
        self.generator.endElement("i")

    def visit_math(self, node):
        self.generator.startElement("m", {})

    def depart_math(self, node):
        self.generator.endElement("m")

    def visit_math_block(self, node):
        self.generator.startElement("math", {})

    def depart_math_block(self, node):
        self.generator.endElement("math")

    def visit_doctest_block(self, node):
        self.generator.startElement("programlisting",
                                    {"language": "python"})

    def depart_doctest_block(self, node):
        self.generator.endElement("programlisting")

    def visit_strong(self, node):
        self.generator.startElement("b", {})

    def depart_strong(self, node):
        self.generator.endElement("b")

    def visit_title_reference(self, node):
        pass

    def depart_title_reference(self, node):
        pass

    def visit_displaymath(self, node):
        pass

    def depart_displaymath(self, node):
        pass

    def _visit_adomonitions(self, node, label):
        if self.listenv:
            self.adomonienv = self.listenv
            self.listenv = None
            self.newline()
        self.generator.startElement(label, {})

    def _depart_adomonitions(self, node, label):
        if self.adomonienv != None:
            self.listenv = self.adomonienv
            self.adomonienv = None
        self.generator.endElement(label)

    def visit_note(self, node):
        self._visit_adomonitions(node, 'note')

    def depart_note(self, node):
        self._depart_adomonitions(node, 'note')

    def visit_tip(self, node):
        self._visit_adomonitions(node, 'tip')

    def depart_tip(self, node):
        self._depart_adomonitions(node, 'tip')

    def visit_caution(self, node):
        self._visit_adomonitions(node, 'caution')

    def depart_caution(self, node):
        self._depart_adomonitions('caution')

    def visit_warning(self, node):
        self._visit_adomonitions(node, 'warning')

    def depart_warning(self, node):
        self._depart_adomonitions(node, 'warning')

    def visit_topic(self, node):
        self._visit_adomonitions(node, 'topic')

    def depart_topic(self, node):
        self._depart_adomonitions(node, 'topic')

    def visit_admonition(self, node):
        self._visit_adomonitions(node, 'admonition')

    def depart_admonition(self, node):
        self._depart_adomonitions(node, 'admonition')

    def visit_unknown_visit(self, node):
        pass

    def depart_unknown_visit(self, node):
        pass

    def visit_number_reference(self, node):
        attrs = {}
        if 'refid' in node.attributes:
            attrs['refid'] = node['refid']
        self.generator.startElement('numref', attrs)

    def depart_number_reference(self, node):
        self.generator.endElement('numref')

    def visit_literal_block(self, node):
        self.generator.startElement('pre', {})
        if "highlight_args" in node.attributes.keys() and node.attributes["linenos"] == "True":
            self.generator.startElement(
                "listinfo",
                {"language": node.attributes["language"]})
            self._lit_block_tag = "listinfo"
        else:
            self.generator.startElement("list", {'type': 'emlist'})
            self._lit_block_tag = "list"
        self.newline()

    def depart_literal_block(self, node):
        self.newline()
        self.generator.endElement(self._lit_block_tag)
        del self._lit_block_tag
        self.generator.endElement('pre')
        self.newline()

    def visit_literal(self, node):
        self.generator.startElement('tt', {'type': 'inline-code'})

    def depart_literal(self, node):
        self.generator.endElement('tt')

    def visit_comment(self, node):
        raise nodes.SkipNode

    def depart_comment(self, node):
        pass

    def visit_compound(self, node):
        pass

    def depart_compound(self, node):
        pass

    def visit_compact_paragraph(self, node):
        pass

    def depart_compact_paragraph(self, node):
        pass

    def visit_figure(self, node):
        self.generator.startElement('figure', {'id':node['ids'][0]})
        
    def depart_figure(self, node):
        self.generator.endElement('figure')

    def visit_image(self, node):
        filename = node['uri']
        if node.get('inline'):
            self.generator.startElement('a', {"linkurl": filename})
        else:
            self.generator.startElement('Image', {'href': filename})

    def depart_image(self, node):
        if node.get('inline'):
            self.generator.endElement('a')
        else:    
            self.generator.endElement('Image')

    def visit_caption(self, node):
        self.generator.startElement('caption', {})
        self.add_fignumber(node.parent)

    def depart_caption(self, node):
        self.generator.endElement('caption')

    def visit_legend(self, node):
        pass

    def depart_legend(self, node):
        pass

    def visit_bullet_list(self, node):
        self.listlevel += 1
        if self.listlevel == 1:
            listenv = "ul"
        elif self.listlevel == 2:
            listenv = 'ul2'
        else:
            logger.info('logging level upper 3')
            listenv = 'ul3'
        self.generator.startElement(listenv, {})
        self.listenv = listenv
        self.newline()

    def depart_bullet_list(self, node):
        self.generator.endElement(self.listenv)
        self.listlevel = self.listlevel - 1
        if self.listlevel == 0:
            self.listenv = None
        elif self.listlevel == 1:
            self.listenv = "ul"
        elif self.listlevel >= 2:
            self.listenv = "ul2"
        self.newline()

    def visit_enumerated_list(self, node):
        self.listenv = "ol"
        if 'start' in node.attributes:
            self.generator.startElement("ol", {'start': str(node['start'])})
        else:
            self.generator.startElement("ol", {})
        self.newline()

    def depart_enumerated_list(self, node):
        self.listenv = None
        self.generator.endElement("ol")

    def visit_reference(self, node):
        atts = {'class': 'reference'}
        if node.get('internal') or 'refuri' not in node:
            atts['class'] += ' internal'
        else:
            atts['class'] += ' external'
        if 'refuri' in node:
            #if node['refuri'] != '':
            #    raise
            atts['href'] = node['refuri'] or '#'
        else:
            assert 'refid' in node, \
                   'References must have "refuri" or "refid" attribute.'
            atts['href'] = '#' + node['refid']
        if not isinstance(node.parent, nodes.TextElement):
            assert len(node) == 1 and isinstance(node[0], nodes.image)
            atts['class'] += ' image-reference'
        if 'reftitle' in node:
            atts['title'] = node['reftitle']
        if 'target' in node:
            atts['target'] = node['target']
        self.generator.startElement("ref", atts)

        if node.get('secnumber'):
            self.generator.outf.write('%s' % '.'.join(map(str, node['secnumber'])))

    def depart_reference(self, node):
        self.generator.endElement("ref")


    def visit_list_item(self, node):
        style = ""
        if self.listenv:
            style = self.listenv + "-item"
        self.generator.startElement("li", {"aid:pstyle": style})

    def depart_list_item(self, node):
        self.generator.endElement("li")
        self.newline()

    def visit_field_list(self, node):
        self.generator.startElement("variablelist", {})

    def depart_field_list(self, node):
        self.generator.endElement("variablelist")

    def visit_field(self, node):
        self.generator.startElement("varlistentry", {})

    def depart_field(self, node):
        self.generator.endElement("varlistentry")

    def visit_field_name(self, node):
        self.generator.startElement("term", {})

    def depart_field_name(self, node):
        self.generator.endElement("term")

    def visit_field_body(self, node):
        self.generator.startElement("listitem", {})

    def depart_field_body(self, node):
        self.generator.endElement("listitem")

    def visit_definition_list(self, node):
        self.listenv = "dl"
        self.generator.startElement("dl", {})
        self.newline()

    def depart_definition_list(self, node):
        self.listenv = None
        self.generator.endElement("dl")
        self.newline()

    def visit_definition_list_item(self, node):
        pass
#        self.generator.startElement("dt", {})

    def depart_definition_list_item(self, node):
        pass
#        self.generator.endElement("dt")
#        self.newline()

    def visit_term(self, node):
        pass
        self.generator.startElement("dt", {})

    def depart_term(self, node):
        pass
        self.generator.endElement("dt")
        self.newline()

    def visit_definition(self, node):
        self.generator.startElement("dd", {})

    def depart_definition(self, node):
        self.generator.endElement("dd")
        self.newline()

    def visit_block_quote(self, node):
        self.generator.startElement("quote", {})
        self.newline()

    def depart_block_quote(self, node):
        self.generator.endElement("quote")
        self.newline()

    def visit_inline(self, node):
        pass
        # if 'xref' in node['classes'] or 'term' in node['classes']:
        #     self.add_text('*')

    def depart_inline(self, node):
        pass
        # if 'xref' in node['classes'] or 'term' in node['classes']:
        #     self.add_text('*')

    def visit_todo_node(self, node):
        raise nodes.SkipNode
        # self.generator.startElement("todo", {})

    def depart_todo_node(self, node):
        # self.generator.endElement("todo")
        pass

    def visit_container(self, node):
        if 'literal-block-wrapper' in node['classes']:
            self.generator.startElement('codelist', {})

    def depart_container(self, node):
        if 'literal-block-wrapper' in node['classes']:
            self.generator.endElement('codelist')

    def visit_citation(self, node):
        self.generator.startElement('a', {})
        self.generator.outf.write(node.rawsource)
        #print(node.__dict__)

    def depart_citation(self, node):
        self.generator.endElement('a')

    def visit_label(self, node):
        self.generator.startElement('label', {})

    def depart_label(self, node):
        self.generator.endElement('label')

    def visit_footnote(self, node):
        # omit node if marked as 'obsolated' (this is added in transforms.py)
        if 'obsolated' in node['classes']:
            raise nodes.SkipNode
        self.generator.startElement("footnote", {'id': node['ids'][0]})
        node.children.remove(node.children[0])

    def depart_footnote(self, node):
        self.generator.endElement('footnote')

    def visit_footnote_reference(self, node):
        raise nodes.SkipNode
        #self.generator.startElement("footnote_reference", {'refid': node['refid']})
        # node.children.remove(node.children[0])

    def depart_footnote_reference(self, node):
        pass
        #self.generator.endElement("footnote_reference")

    def visit_substitution_definition(self, node):
        pass

    def depart_substitution_definition(self, node):
        pass

    def visit_table(self, node):
        self.tableenv = True
        self.cols = 0
        self.generator.startElement('table', {})

    def depart_table(self, node):
        self.generator.endElement('table')
        self.tableenv = False

    def visit_tgroup(self, node):
        #self.generator.startElement('tgroup', {})
        pass

    def depart_tgroup(self, node):
        #self.generator.endElement('tgroup')
        pass

    def visit_colspec(self, node):
        #self.generator.startElement('colspec', {})
        pass

    def depart_colspec(self, node):
        # self.generator.endElement('colspec')
        pass

    def visit_thead(self, node):
        self.generator.startElement('thead', {'aid:pstyle': 'header'})

    def depart_thead(self, node):
        self.generator.endElement('thead')

    def visit_row(self, node):
        # self.generator.startElement('tr', {})
        pass

    def depart_row(self, node):
        # self.generator.endElement('tr')
        pass

    def visit_line_block(self, node):
        pass

    def depart_line_block(self, node):
        pass

    def visit_line(self, node):
        pass

    def depart_line(self, node):
        pass

    def visit_entry(self, node):
        self.generator.startElement('td', {
                'aid:table': 'cell',
                'aid:crows': '1',
                'aid:ccols': '1'
            })

    def depart_entry(self, node):
        self.generator.endElement('td')
        #self.generator.outf.write('\t')

    def visit_tbody(self, node):
        tcol = str(node.parent.attributes['cols'])
        trow = str(len(node.children))
        self.generator.startElement('tbody',
            {
                'aid:tcols': tcol,
                'aid:trows': trow,
                'aid:table': 'table'
            })

    def depart_tbody(self, node):
        self.generator.endElement('tbody')

    def visit_problematic(self, node):
        pass

    def depart_problematic(self, node):
        pass

    def visit_citation(self, node):
        self.generator.startElement('a', {})
        self.generator.outf.write(node.rawsource)
        #print(node.__dict__)

    def depart_citation(self, node):
        self.generator.endElement('a')

    def visit_label(self, node):
        self.generator.startElement('label', {})

    def depart_label(self, node):
        self.generator.endElement('label')

    def visit_footnote_reference(self, node):
        self.generator.startElement('footnote', {'href': node['refid']})

    def depart_footnote_reference(self, node):
        self.generator.endElement('footnote')

    def visit_substitution_definition(self, node):
        pass

    def depart_substitution_definition(self, node):
        pass

    def visit_table(self, node):
        self.tableenv = True
        self.generator.startElement('table', {})

    def depart_table(self, node):
        self.generator.endElement('table')
        self.tableenv = False

    def visit_tgroup(self, node):
        #self.generator.startElement('tgroup', {})
        pass

    def depart_tgroup(self, node):
        #self.generator.endElement('tgroup')
        pass

    def visit_colspec(self, node):
        self.generator.startElement('colspec', {})

    def depart_colspec(self, node):
        self.generator.endElement('colspec')

    def visit_thead(self, node):
        self.generator.startElement('thead', {'aid:pstyle': 'header'})

    def depart_thead(self, node):
        self.generator.endElement('thead')

    def visit_row(self, node):
        self.generator.startElement('tr', {})

    def depart_row(self, node):
        self.generator.endElement('tr')

    def visit_entry(self, node):
        #self.generator.startElement('entry', {})
        pass

    def depart_entry(self, node):
        #self.generator.endElement('entry')
        self.generator.outf.write('\t')

    def visit_tbody(self, node):
        self.generator.startElement('tbody', {})

    def depart_tbody(self, node):
        self.generator.endElement('tbody')

    def visit_problematic(self, node):
        pass

    def depart_problematic(self, node):
        pass

    def visit_superscript(self, node):
        self.generator.startElement('sup', {})

    def depart_superscript(self, node):
        self.generator.endElement('sup')

    def visit_column(self, node):
        self.generator.startElement('column', {})
        self.generator.outf.write('<title aid:pstyle="column-title" id="%s">%s</title>' % (node['ids'], node['title']))

    def depart_column(self, node):
        self.generator.endElement('column')

    def visit_raw(self, node):
        self.generator.startElement('raw', {})

    def depart_raw(self, node):
        self.generator.endElement('raw')

    def visit_transition(self, node):
        self.generator.startElement('transition', {})

    def depart_transition(self, node):
        self.generator.endElement('transition')



class SingleIndesignVisitor(IndesignVisitor):
    sec_level = 0

    def visit_start_of_file(self, node):
        pass

    def depart_start_of_file(self, node):
        self.newline()

    def visit_document(self, node):
        self.generator.startDocument()
        # only occurs in the single-file builder
        self.generator.outf.write(
            '<doc xmlns:aid="http://ns.adobe.com/AdobeInDesign/4.0/">')
        self.newline()

    def depart_document(self, node):
        self.generator.endDocument()
        self.generator.outf.write("</doc>")
