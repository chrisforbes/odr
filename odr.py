#!/usr/bin/env python2

import zipfile
import sys
import xml.sax

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
            print u"%s%s" % (indent,self.content)
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
    src = sys.argv[1]
    print "loading %s" % (src)
    zf = zipfile.ZipFile(src)
    content = zf.read('content.xml')
    xml.sax.parseString(content, FormattingHandler())

if __name__ == '__main__':
    main()
