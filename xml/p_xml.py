#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from lxml import etree

f = 'sitemap-index.xml'


# parser = etree.XMLParser(load_dtd = True)
# tree = etree.parse(f, parser)

tree = etree.parse(f)

root = tree.getroot()

# print root

# sys.exit(0)
for row in root:
    for field in row:
        if field.text.
        print field.tag
        print field.text

