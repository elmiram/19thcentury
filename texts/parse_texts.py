# coding=utf-8

import sys, os, codecs
import re
import json, uuid
# note: the path is hardcoded on the next line. change accordingly.
sys.path.append('C:/Users/Admin/OneDrive/PycharmProjects/learner_corpus/learner_corpus')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from annotator.models import Document, Sentence, Token, Morphology, Annotation
import django
django.setup()

reSpace = re.compile(u'\\s+',flags=re.U)

students = []

class Struct:
    def __init__(self, **values):
        vars(self).update(values)

    def makesent(self):
        result = u''
        for num in range(len(self.words)):
            if num != 0:
                if self.words[num].punctl != self.words[num - 1].punctr:
                    result += self.words[num].punctl
                result += self.words[num].text + self.words[num].punctr + ' '
            else:
                result += self.words[num].punctl + self.words[num].text + self.words[num].punctr + ' '
        self.sentence = reSpace.sub(' ', result)
        # print self.sentence


def make_tagged_sent(words):
    result = u''
    for num in range(len(words)):
        tooltip, punctl, token, punctr = words[num][0], words[num][1], words[num][2], words[num][3]
        if num != 0:
            if punctl != words[num - 1][3]:
                result += punctl
            result += '<span class="token" data-toggle="tooltip" title="' + tooltip + '">' + token + '</span>' + punctr + ' '
        else:
            result += punctl + '<span class="token" data-toggle="tooltip" title="' + tooltip + '">' + token + '</span>' + punctr + ' '
    return result

def split_err_from_gram(tags):
    tags = tags.split(' ')
    errors = ["lex.word", "contr", "lex.constr", "infl", "typo", "coord", "discouse", "le", "logic", "disocourse", "comparlex", "colloq", "phrase", "nmz", "intens", "pron", "disccourse", "asp", "styll", "couse", "gov", "disourse", "prep", "constr", "tauto", "dscourse", "official", "compar", "cause", "parc", "intence", "cit", "lack", "dicourse", "lex", "contam", "connector", "ref", "agr", "phraze", "solloq", "les", "styl", "tense", "consrt", "caus", "derive", "lec", "meton", "coloq", "voice", "intense", "paron", "offficial", "caus:typo", "rel_clause", "discours", "concord", "discuorse", "sent_arg", "topic", "consrtr", "word", "arg", "converb", "dis_coord", "discourse", "aux", "contsr", "wo", "ref_clause", "tauot", "link", "discorse", "fef", "deriv"]
    gram = []
    err = []
    for tag in tags:
        if tag not in errors:
            gram.append(tag)
        else:
            err += correct_tags(tag)
    # print err
    return ' '.join(gram), err


def correct_tags(tag):
    dict = {'lex.word': ['lex', 'word'],
            'lex.constr': ['lex', 'constr'],
            'discouse': ['discourse'],
            'le': ['lex'],
            'disocourse': ['discourse'],
            'comparlex': ['compar', 'lex'],
            'disccourse': ['discourse'],
            'styll': ['styl'],
            'couse': ['cause'],
            'dscourse': ['discourse'],
            'intence': ['intens'],
            'dicourse': ['discourse'],
            'phraze': ['phrase'],
            'solloq': ['colloq'],
            'les': ['lex'],
            'consrt': ['constr'],
            'derive': ['deriv'],
            'lec': ['lex'],
            'coloq': ['colloq'],
            'offficial': ['official'],
            'caus:typo': ['caus', 'typo'],
            'discours': ['discourse'],
            'discuorse': ['discourse'],
            'consrtr': ['constr'],
            'arg': ['agr'],
            'contsr': ['constr'],
            'discorse': ['discourse'],
            'fef': ['ref']
            }
    return dict[tag] if tag in dict.keys() else [tag]


def tooltip_generator(anas):
    d = {}
    for ana in anas:
        lem = ana.lem
        bastard = False
        if 'qual="' in lem:
            lem = lem.split('"')[0]
            bastard = True
        lex, gram = ','.join(ana.lex.split(' ')), ','.join(ana.gram.split(' '))
        if bastard:
            lex = 'bastard,' + lex
        if lem + ', ' + lex not in d:
            d[lem + ', ' + lex] = gram
        else:
            d[lem + ', ' + lex] += '<br>' + gram
    arr = ['<b>'+key+'</b><br>' + d[key] for key in d]
    return '<hr>'.join(arr)
    # todo generate tooltip with morpho <- merge similar morphos!!


def get_prs(fname):
    prs = codecs.open(fname, 'r', 'utf-8')
    meta = {}
    sents = []
    prev_sentno = 0
    prev_wordno = 0
    for line in prs:
        if line.startswith('#sentno') or line.startswith('#meta.issue') or line.startswith('#meta.docid'):
            continue
        line = line.strip('\r\n')
        if line.startswith('#'):
            field, value = line[6:].split('\t')
            meta[field.replace('-', '_')] = value
            if meta['author'] != '':
                if meta['author'] in students:
                    student_code = students.index(meta['author']) + 1
                else:
                    students.append(meta['author'])
                    student_code = len(students)
            else:
                student_code = 0
            meta['student_code'] = student_code
            if field in ['date1', 'date2', 'words', 'sentences', 'university-code', 'term', 'module']:
                if value == u'':
                    meta[field.replace('-', '_')] = 0
                else:
                    meta[field.replace('-', '_')] = int(re.search('\\d+', value).group())
        else:
            sentno, wordno, lang, graph, word, indexword, nvars, nlems, nvar, lem, trans, trans_ru, lex, gram, flex, punctl, punctr, sent_pos = line.split('\t')
            # print wordno, prev_wordno
            gram, err = split_err_from_gram(gram)
            ana = Struct(lem='', lex='', gram='', err=[])
            if nvar <= nvars:
                ana = Struct(lem=lem, lex=lex, gram=gram, err=err)
            if sentno != prev_sentno:
                if wordno != prev_wordno:
                    # print 'nw'
                    w = Struct(num=wordno,text=word,
                        punctl=punctl,punctr=punctr,sent_pos=sent_pos, ana=[ana])
                else:
                    w.ana.append(ana)
                sents.append(Struct(num=sentno,words=[w]))
            else:
                if wordno != prev_wordno:
                    # print word
                    w = Struct(num=wordno, text=word,
                               punctl=punctl, punctr=punctr, sent_pos=sent_pos, ana=[ana])
                    sents[-1].words.append(w)
                else:
                    w.ana.append(ana)

            if sent_pos == 'eos' and nvars == nvar:
                prev_wordno = 0
            else:
                prev_wordno = wordno
            prev_sentno = sentno
            # print len(sents[-1].words)
    meta["body"] = ''
    print(meta)
    prs.close()
    doc, created = Document.objects.get_or_create(**meta)
    doc.filename = fname.replace(u'D:\Документы\Рабочий стол\parsed_data\\', '')
    for i in xrange(len(sents)):
        sents[i].makesent()
        print '.',
        sent, created = Sentence.objects.get_or_create(text=sents[i].sentence,
                                              doc_id=doc,
                                              num=i)
        stagged = []
        for k in range(len(sents[i].words)):
            w = sents[i].words[k]
            word, created = Token.objects.get_or_create(token=w.text,
                                               doc=doc,
                                               sent=sent,
                                               num=w.num,
                                               punctl=w.punctl, punctr=w.punctr, sent_pos=w.sent_pos)

            for a in w.ana:
                Morphology.objects.get_or_create(token=word, lem=a.lem, lex=a.lex, gram=a.gram)
            tok = (tooltip_generator(w.ana), word.punctl, word.token, word.punctr)
            # if k != len(sents[i].words) - 1:
            #     offset = len(word.punctl + word.token + word.punctr+ '</span>' '<span class="token" data-toggle="tooltip" title="') + len(tooltip_generator(sents[i].words[k+1].ana) + '">')
            # else:
            #     offset = 100
            if w.ana[0].err != []:
                annot, created = Annotation.objects.get_or_create(document=sent, guid=str(uuid.uuid4()),
                                                 data=json.dumps({"ranges": [{"start": "/span["+str(k+1)+"]", "end": "/span["+str(k+1)+"]", "startOffset": 0, "endOffset": len(word.punctl + word.token + word.punctr)}], "quote": w.text, "text": "", "tags": w.ana[0].err}))
                d = json.loads(annot.data)
                d['readonly'] = False
                annot.data = json.dumps(d)
                annot.tag = ', '.join(w.ana[0].err)
                annot.start = str(k+1)
                annot.end = str(k+1)
                annot.save()
                doc.annotated = True
                doc.body = 'loaded from xml'
                doc.save()
            stagged.append(tok)
        sent.tagged = make_tagged_sent(stagged)
        sent.save()
    print len(sents)




if __name__ == "__main__":
    for root, dirs, files in os.walk(u'D:\Документы\Рабочий стол\parsed_data\\all'):
        for i in files:
            if i.endswith('.prs'):
                p = os.path.join(root, i)
                print
                print p
                get_prs(p)
