#!/usr/bin/env python2

import zipfile
import sys
import xml.sax
import textwrap
import re

class FormattingHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.content = ''
        self.styles = []
        self.stats = {}

    def emit_queued_content(self):
        indent = ''
        t = None
        for s in self.styles:
            if s == u'text:p' and t != u'text:list-item':
                indent += ' '
            if s == u'text:list-item':
                indent += ' * '
            t = s;
        if len(self.content):
            tr = textwrap.TextWrapper()
            tr.initial_indent = indent
            tr.subsequent_indent = re.sub('.', ' ', indent);
            for l in tr.wrap(self.content):
                print l
            self.content = ''

    def startElement(self,name,attr):
        if name == u'text:span': return
        self.emit_queued_content()

        # establish new style TODO TODO TODO
        self.styles.append(name)
        self.stats[name] = self.stats.get(name,0) + 1

    def endElement(self,name):
        if name == u'text:span': return
        self.emit_queued_content()
        self.styles.pop()

    def characters(self, content):
        self.content += content

    def endDocument(self):
        if '--debug' in sys.argv:
            print self.stats

def main():
    if len(sys.argv) < 2:
        print "usage: odr <file> [--debug]"
        return 1

    src = sys.argv[1]
    print "loading %s" % (src)
    zf = zipfile.ZipFile(src)
    content = zf.read('content.xml')
    xml.sax.parseString(content, FormattingHandler())
    return 0

if __name__ == '__main__':
    sys.exit(main())
