# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ug_QMmZp21OitoCbqERCxJytSFQB_Eei
"""

p = 0
h = 0
for i in range(20):
  with open('/content/drive/MyDrive/input/Field{}.txt'.format(i+1), mode='r') as file:
    text = file.read()
    k = text[1:len(text)-1].replace(', (', '*(').split('*')
    sp = []
    for j in k:
      f = list(map(int, j.replace('(', '').replace(')', '').split(', ')))
      sp.append(f)
    for j in range(len(sp)-1):
      p += sp[j][0] * sp[j + 1][1]
      h += sp[j + 1][0] * sp[j][1]
    p += sp[-1][0] * sp[0][1]
    h += sp[0][0] * sp[-1][1]
    print(abs(p - h) * 0.5)