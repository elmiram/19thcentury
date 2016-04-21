# coding=utf-8
import sys, os, codecs, datetime
sys.path.append('C:/Users/Admin/OneDrive/PycharmProjects/learner_corpus/learner_corpus')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
# /home/elmira/learner_corpus/
from annotator.models import Morphology
import django
django.setup()


def func1():
    for sep in [',', ' ']:
        s = Morphology.objects.filter(lex__contains=sep)
        count = s.count()
        print count
        num = 0
        for obj in s:
            num += 1
            lex = obj.lex.split(sep)
            if 'bastard' in lex:
                obj.gram += ',bastard'
                lex = lex[1:]
            obj.gram += ',' + ','.join(lex[1:])
            obj.lex = lex[0]
            obj.save()
            if num % 1000 == 0:
                print num, 'of', count, int(100*float(num)/count)


def func2():
    with codecs.open(u'LEX_FIELD.CSV', 'r', 'utf-8') as f:
        for line in f:
            if line.startswith('S') or line.startswith('V'):
                line = line.strip()
                print datetime.datetime.now().time(), line
                if ' ' in line:
                    lex = line.split(' ')
                    gram = ',' + ','.join(lex[1:])
                    lex = lex[0]
                elif ',' in line:
                    lex = line.split(',')
                    gram = ',' + ','.join(lex[1:])
                    lex = lex[0]
                else:
                    continue
                s = Morphology.objects.filter(lex=line)
                count = s.count()
                print count
                num = 0
                for obj in s:
                    num += 1
                    obj.gram += gram
                    # print obj.gram
                    obj.lex = lex
                    # print obj.lex
                    obj.save()
                    if num % 5000 == 0:
                        print num, 'of', count, int(100*float(num)/count), datetime.datetime.now().time()


def func3():
    with codecs.open(u'LEX_FIELD.CSV', 'r', 'utf-8') as f:
        for line in f:
            if line.startswith('S') or line.startswith('V'):
                line = line.strip()
                # print datetime.datetime.now().time(), line
                if ' ' in line:
                    lex = line.split(' ')
                    gram = ',' + ','.join(lex[1:])
                    lex = lex[0]
                elif ',' in line:
                    lex = line.split(',')
                    gram = ',' + ','.join(lex[1:])
                    lex = lex[0]
                else:
                    continue
                print 'UPDATE annotator_morphology SET lex="'+lex+'", gram=gram ||"'+gram+'" WHERE lex="'+line+'";'
func3()

# UPDATE `docs` SET `author`="-",`title`="эссе (журналист, 2 курс бак)", `date1`="2013", `date2`="2014", `genre`="эссе", `gender`="ж", `major`="журналист", `course`="2 курс бак", `date_displayed`="2013–2014",  `term`="2", `module`="3", `domain`="разнородная тематика", `words`=1068 WHERE `filename` LIKE "%../languages/academrussian/parsed_data//text_2014//tekstyNCh16marta//Sobranieoshibokjanvar2014//Kozkina.Esse246zh.prs%";