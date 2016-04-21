# coding=utf-8

__author__ = 'elmira'
import uuid
import re
import HTMLParser
import subprocess
import codecs
import os

PATH_TO_MYSTEM = '/home/elmira/learner_corpus/mystem'  # todo CHANGE THAT TO mystem for unix
regSe = re.compile(u'<se>(.*?)</se>', flags=re.U | re.DOTALL)
regWord = re.compile(u'^(.*?)<w>(.*?)(<ana.*/>)?</w>(.*)$', flags=re.U)
regAna = re.compile(u'<ana lex="(.*?)" gr="(.*?)" />', flags=re.U)


class Word:
    def __init__(self, pl, wf, anas, pr, ttip):
        self.pl, self.wf, self.anas, self.pr, self.tooltip = pl, wf, anas, pr, ttip


class Sent:
    def __init__(self, text, words):
        self.text, self.words = text, words


def mystem(text):
    fname = 'temp' + str(uuid.uuid4()) + '.txt'
    f = codecs.open(fname, 'w', 'utf-8')
    f.write(text.replace('\r\n', '\r').replace('\n', '\r'))
    f.close()
    args = [PATH_TO_MYSTEM, '-cnisd', '--format', 'xml', '--eng-gr', fname]  # Temp+ hash, del temp
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    output = p.stdout.read()  # this is mystem xml
    # print output
    os.remove(fname)
    output = get_sentences(output)  # returns tuple (num of words, arr of sents), each sent has .text and .words=array
    return output


def get_sentences(xml):
    arr = [i.strip().split('\n') for i in regSe.findall(xml)]
    words = 0  # how many words
    T = []
    for se in arr:
        se_text = ''
        se_words = []
        for word in se:
            search = regWord.search(word)
            if search is None:
                continue
            words += 1
            if search is None: print word
            punctl, wordform, anas, punctr = search.group(1), search.group(2), search.group(3), search.group(4).replace('\r', ' ')
            if anas:
                anas = regAna.findall(anas)  # массив пар, в каждой паре - лемма + разбор
            else:
                anas = []
            tooltip = tooltip_generator(anas)
            W = Word(punctl, wordform, anas, punctr, tooltip)
            se_words.append(W)
            se_text += punctl + wordform + punctr
        S = Sent(se_text, se_words)
        T.append(S)
    return words, T


def tooltip_generator(anas):
    print anas
    d = {}
    for ana in anas:
        lem = ana[0]
        bastard = False
        if 'qual="' in lem:
            lem = lem.split('"')[0]
            bastard = True
        lex, gram = ana[1].split('=')
        if bastard:
            lex = 'bastard,' + lex
        if lem + ', ' + lex not in d:
            d[lem + ', ' + lex] = gram
        else:
            d[lem + ', ' + lex] += '<br>' + gram
    arr = ['<b>'+key+'</b><br>' + d[key] for key in d]
    return '<hr>'.join(arr)
    # todo generate tooltip with morpho <- merge similar morphos!!
