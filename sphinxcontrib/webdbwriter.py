# -*- coding: utf-8 -*-

from docutils.writers import Writer
from docutils import nodes
from docutils.nodes import NodeVisitor
from xml.sax.saxutils import XMLGenerator
from six import StringIO

import os.path
import os


class WebDBXMLWriter(Writer):
    def __init__(self, builder, single=False):
        Writer.__init__(self)
        self.single = single
        self.builder = builder

    def translate(self):
        if self.single:
            self.visitor = visitor = SingleWebDBXMLVisitor(self.document)
        else:
            self.visitor = visitor = WebDBXMLVisitor(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()

class WebDBXMLVisitor(NodeVisitor):
    def __init__(self, document):
        NodeVisitor.__init__(self, document)

        self._output = StringIO()
        self.generator = XMLGenerator(self._output, "utf-8")
        self.generator.outf = self._output

        self.listenv = None
        self.within_index = False
        self.licount = 0

    def newline(self):
        self.generator.outf.write("\n")

    def astext(self):
        return self._output.getvalue()

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
        if not self.listenv:
            self.generator.startElement('p', {'aid:pstyle': u'本文'})

    def depart_paragraph(self, node):
        if not self.listenv:
            self.generator.endElement('p')
            self.newline()

    def visit_section(self, node):
        assert not self.within_index
        self.sec_level += 1

    def depart_section(self, node):
        self.sec_level -= 1
        self.newline()

    def visit_title(self, node):
        level = ""
        if self.sec_level == 1:
            level = u"大見出し"
        elif self.sec_level == 2:
            level = u"中見出し"
        elif self.sec_level == 3:
            level = u"小見出し"

        self.generator.startElement('title', 
                                    {"aid:pstyle": level})

    def depart_title(self, node):
        self.generator.endElement('title')
        dtp = u'<?dtp level="{0}" section="{1}"?>'.format(
            self.sec_level + 1,
            node.astext(),
        )
        self.generator.outf.write(dtp.encode('utf-8'))

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
        # self.generator.startElement('section', {})
        pass

    def depart_target(self, node):
        pass

    def visit_emphasis(self, node):
        self.generator.startElement("emphasis", {})

    def depart_emphasis(self, node):
        self.generator.endElement("emphasis")

    def visit_math(self, node):
        pass

    def depart_math(self, node):
        pass

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

    def visit_note(self, node):
        self.generator.startElement('note', {})

    def depart_note(self, node):
        self.generator.endElement('note')

    def visit_tip(self, node):
        self.generator.startElement('tip', {})

    def depart_tip(self, node):
        self.generator.endElement('tip')

    def visit_warning(self, node):
        self.generator.startElement('warning', {})

    def depart_warning(self, node):
        self.generator.endElement('warning')

    def visit_unknown_visit(self, node):
        pass

    def depart_unknown_visit(self, node):
        pass


    def visit_number_reference(self, node):
        pass

    def depart_number_reference(self, node):
        pass
        
    def visit_literal_block(self, node):
        if "highlight_args" in node.attributes.keys():
            self.generator.startElement(
                "listinfo",
                {'aid:cstyle': u"リスト",
                 "language": node.attributes["language"]})
            self._lit_block_tag = "listinfo"
        else:
            self.generator.startElement("literal", {'aid:cstyle': u"コマンド"})
            self._lit_block_tag = "literal"
        self.newline()

    def depart_literal_block(self, node):
        self.newline()
        self.generator.endElement(self._lit_block_tag)
        del self._lit_block_tag
        self.newline()

    def visit_literal(self, node):
        self.generator.startElement("literal", {'aid:cstyle': u"コマンド"})

    def depart_literal(self, node):
        self.generator.endElement("literal")

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
        pass

    def depart_figure(self, node):
        pass

    def visit_image(self, node):
        pass

    def depart_image(self, node):
        pass

    def visit_reference(self, node):
        pass

    def depart_reference(self, node):
        pass

    def visit_caption(self, node):
        pass

    def depart_caption(self, node):
        pass

    def visit_bullet_list(self, node):
        self.generator.startElement('p', {'aid:pstyle': u'半行アキ'})
        self.generator.endElement('p')
        self.listenv = "ul"
        self.generator.startElement("ul", {})
        self.newline()

    def depart_bullet_list(self, node):
        self.listenv = None
        self.licount = 0
        self.generator.endElement("ul")
        self.generator.startElement('p', {'aid:pstyle': u'半行アキ'})
        self.generator.endElement('p')
        self.newline()

    def visit_enumerated_list(self, node):
        self.generator.startElement('p', {'aid:pstyle': u'半行アキ'})
        self.generator.endElement('p')
        self.listenv = "ol"
        self.generator.startElement("ol", {})
        self.newline()

    def depart_enumerated_list(self, node):
        self.listenv = None
        self.licount = 0
        self.generator.endElement("ol")
        self.generator.startElement('p', {'aid:pstyle': u'半行アキ'})
        self.generator.endElement('p')
        self.newline()

    def visit_reference(self, node):
        atts = {'class': 'reference'}
        if node.get('internal') or 'refuri' not in node:
            atts['class'] += ' internal'
        else:
            atts['class'] += ' external'
        if 'refuri' in node:
            atts['href'] = node['refuri']
        else:
            assert 'refid' in node, \
                   'References must have "refuri" or "refid" attribute.'
            atts['href'] = '#' + node['refid']
        if not isinstance(node.parent, nodes.TextElement):
            assert len(node) == 1 and isinstance(node[0], nodes.image)
            atts['class'] += ' image-reference'
        if 'reftitle' in node:
            atts['title'] = node['reftitle']
#        self.generator.startElement("footnote", atts)
#        self.generator.endElement("footnote")

#        if node.get('secnumber'):
#            self.body.append(('%s' + self.secnumber_suffix) %
#                             '.'.join(map(str, node['secnumber'])))

    def visit_footnote(self, node):
        pass
#        self.generator.startElement("footnote", {})

    def depart_footnote(self, node):
        pass
#        self.generator.endElement("footnote")
        self.newline()

    def visit_list_item(self, node):
        self.licount += 1
        self.generator.startElement("li", {"aid:pstyle": u"箇条書き"})
        if self.listenv == "ul":
            self.generator.outf.write("・")
        else:
            self.generator.outf.write("{}. ".format(self.licount))
            

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
        self.generator.startElement('p', {'aid:pstyle': u'半行アキ'})
        self.generator.endElement('p')
        self.listenv = "dl"
        self.generator.startElement("dl", {})
        self.newline()

    def depart_definition_list(self, node):
        self.listenv = None
        self.licount = 0
        self.generator.endElement("dl")
        self.generator.startElement('p', {'aid:pstyle': u'半行アキ'})
        self.generator.endElement('p')
        self.newline()

    def visit_definition_list_item(self, node):
        pass
#        self.generator.startElement("dt", {"aid:pstyle": u"箇条書き"})

    def depart_definition_list_item(self, node):
        pass
#        self.generator.endElement("dt")
#        self.newline()

    def visit_term(self, node):
        self.generator.startElement("dt", {'aid:pstyle': u"箇条書き"})

    def depart_term(self, node):
        self.generator.endElement("dt")
        self.newline()

    def visit_definition(self, node):
        self.generator.startElement("dd", {'aid:pstyle': u"箇条書き説明"})

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
        if 'xref' in node['classes'] or 'term' in node['classes']:
            self.add_text('*')

    def depart_inline(self, node):
        if 'xref' in node['classes'] or 'term' in node['classes']:
            self.add_text('*')

    def visit_todo_node(self, node):
        pass

    def depart_todo_node(self, node):
        pass

    def visit_container(self, node):
        pass
    
    def depart_container(self, node):
        pass

class SingleWebDBXMLVisitor(WebDBXMLVisitor):
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
