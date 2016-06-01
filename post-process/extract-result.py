# -*- coding: utf-8 -*-

from sys import stdin
from re import search

for line in stdin:
    line = line.strip()
    if not search("###", line):
        print line
