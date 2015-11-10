#!/usr/bin/env python
# -*- coding: utf-8 -*-


l = []
with open("../pinyin.txt") as f:
	for line in f:
		l.append(line.replace("\n", ""))

f.close()

f = open("../pinyin_re2.txt", "a+")

for i in l:
	for j in l:
		s = ""
		for k in l:
			# s = i+j+k+"\n"
			s = s + i+j+k+"\n"
			# print s
		f.writelines(s)