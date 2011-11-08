#!/usr/bin/env python2

import zipfile
import sys
import xml.sax
import textwrap
import re

class Sequence(object):   # todo: different sequence numbering methods, etc
    def __init__(self): self.curval = 0
    def nextval(self, fmt):
        self.curval += 1
        if fmt == 'A':
            return '%s.' % (chr(ord('A') + self.curval - 1))    # after Z?
        elif fmt == '1':
            return '%s.' % (self.curval)
        else:
            return '??'     # at least roman numerals are specified in ODF,
                            # but i haven't needed that yet.

class FormattingHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.content = ''
        self.styles = []
        self.stats = {}
        self.seqs = {}

        self.inline_ignore_elems = [
            u'text:a',
            u'text:span',
            u'text:soft-page-break',
            ]
        self.inline_elems = [
            u'text:s',
            u'text:tab',
            u'text:sequence',
            ]

    def emit_queued_content(self):
        if not len(self.content):
            return

        indent = ''
        t = None
        for s in self.styles:
            if s == u'text:p' and t != u'text:list-item':
                indent += ' '
            if s == u'text:list-item':
                indent += ' * '
            if s == u'text:h':
                self.content = '\33[1m\33[4m' + self.content + '\33[0m'
            t = s;

        tr = textwrap.TextWrapper()
        tr.initial_indent = indent
        tr.subsequent_indent = ' ' * len(indent)
        lines = tr.wrap(self.content)
        for l in lines:
            print l
        print ''
        self.content = ''

    def startElement(self,name,attr):
        if '--xml' in sys.argv:
            self.content += '<%s>' % name

        if name in self.inline_ignore_elems: return

        if name == u'text:tab':
            self.content += '\t'
            return
        if name == u'text:s':
            num_spaces = int(attr.get('text:c','1'))
            self.content += ' ' * num_spaces
            return

        if name == u'text:sequence':
            seq_name = attr.get('text:name','')
            if seq_name not in self.seqs:
                self.seqs[seq_name] = Sequence()
            self.content += self.seqs[seq_name].nextval(
                attr.get('style:num-format','1'))
            return

        self.emit_queued_content()

        self.styles.append(name)
        self.stats[name] = self.stats.get(name,0) + 1

    def endElement(self,name):
        if '--xml' in sys.argv:
            self.content += '</%s>' % name

        if name in self.inline_elems or \
            name in self.inline_ignore_elems: return
        self.emit_queued_content()
        self.styles.pop()

    def characters(self, content):
        self.content += content

    def endDocument(self):
        if '--debug' in sys.argv:
            print self.stats

def main():
    if len(sys.argv) < 2:
        print "usage: odr <file> [--debug] [--xml]"
        return 1

    src = sys.argv[1]
    try:
        zf = zipfile.ZipFile(src)
        contentStream = zf.open('content.xml')
        xml.sax.parse(contentStream, FormattingHandler())
    except IOError: pass            # broken pipe, from exiting the pager
    except KeyboardInterrupt: pass  # ^C
    return 0

if __name__ == '__main__':
    sys.exit(main())
