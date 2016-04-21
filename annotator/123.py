__author__ = 'Admin'
import codecs

with codecs.open(u'gram-fields.csv', 'r', 'utf-8') as f:
    arr = []
    for line in f:
        line = line.strip()
        if ' ' in line:
            line = line.split(' ')
        elif ',' in line:
            line = line.split(',')
        else:
            line = [line]
        for i in line:
            if i not in arr:
                arr.append(i)
    print len(arr)
    for i in arr:
        print i
