# -*- coding=utf-8 -*-
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, render
#from models import Doc, Sentence, Error, Analysis, Token
from annotator.models import Document, Sentence, Annotation, Token, Morphology
from django.views.generic.base import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from forms import QueryForm
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.template import *
from search import *
from collections import Counter
from django.utils.translation import ugettext_lazy as _
import math, json, re
from db_utils import Database



import re
import HTMLParser
import xlsxwriter
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
h = HTMLParser.HTMLParser()
rePage = re.compile(u'&page=\\d+', flags=re.U)
reSpan = re.compile(u'<span class="token"( data-toggle="tooltip")? title=".*?">(.*?)</span>', flags=re.U)

from django.forms.formsets import formset_factory


class Struct:
    def __init__(self, **values):
        vars(self).update(values)


class Index(View):

    def get(self, request, page):
        doc_list = Document.objects.all()
        # эта функция просто достает нужный шаблон и показывает его
        if page == '':
            return render_to_response(u'start.html', {'docs': doc_list}, context_instance=RequestContext(request))
        page = 'simple/' + page + '.html'
        return render_to_response(page, {'docs': doc_list}, context_instance=RequestContext(request))


class PopUp(View):

    def get(self, request, page):
        page = 'search/' + page + '.html'
        return render_to_response(page, context_instance=RequestContext(request))

class Search(Index):
    # тут все для поиска

    # todo write search
    def get(self, request, page):  # page does nothing here, just ignore it
        if len(request.GET) < 1:
            # QueryFormset = formset_factory(QueryForm, extra=2)
            return render_to_response('search.html',
                                      context_instance=RequestContext(request))
        else:
            query = request.GET
            subcorpus, subcorpus_sents, subcorpus_words, flag = get_subcorpus(query)
            # print subcorpus.count()
            # subcorpus_sents = [sent.id for doc in subcorpus[0] for sent in doc.sentence_set.all()]
            count_data = {'total_docs': Document.objects.count(),
                          'total_sents': Sentence.objects.count(),
                          'total_tokens': Token.objects.count(),
                          'subcorpus_docs': len(subcorpus),
                          'subcorpus_sents': subcorpus_sents,
                          'subcorpus_words': subcorpus_words}
            per_page = int(query.get(u'per_page'))
            page = request.GET.get('page')
            page = int(page) if page else 1
            expand = int(query.get(u'expand')[-1])
            if query["exact_word"] != '':
                jq, sent_list, word, res_docs, res_num = exact_search(request.GET["exact_word"].lower().encode('utf-8'), subcorpus, flag, expand, page, per_page)
            else:
                # todo rewrite this part of search
                jq, sent_list, word, res_docs, res_num = lex_search(query, subcorpus, flag, expand, page, per_page)
            paginator = Paginator([''] * res_num, per_page)
            start = page - 10 if page > 10 else 1
            end = page + 10 if page + 10 <= paginator.num_pages else paginator.num_pages
            paginator.page_range2 = range(start, end + 1)
            try:
                sents = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                sents = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                sents = paginator.page(paginator.num_pages)
            full_path = rePage.sub('', request.get_full_path())
            d_path = full_path.replace('19thcentury/search/', '19thcentury/search/download/')
            #word = re.sub('\s', '_', word)
            return render_to_response('result.html',
                                      {'query': word, 'result': sent_list, 'pages': sents,
                                       'numbers': count_data,
                                       'total': res_num, 'total_docs': res_docs,
                                       'path': full_path, 'd_path': d_path, 'j': jq, 'olstart': (page - 1) * per_page + 1},
                                      context_instance=RequestContext(request))

class Statistics(Index):

    def get(self, request, page):
        docs = Document.objects.count()
        doc_ann = Document.objects.filter(annotated=True).count()
        doc_ann_percent = int(100*float(doc_ann)/docs)
        doc_check = Document.objects.filter(checked=True).count()
        doc_check_percent = int(100*float(doc_check)/docs)
        sents = Sentence.objects.count()
        words = Token.objects.count()
        annotations = Annotation.objects.count()
        gender = dict(Counter([i.gender for i in Document.objects.all()]))
        genres = dict(Counter([i.genre for i in Document.objects.all()]))
        # course = dict(Counter([i.course for i in Document.objects.all()]))
        # major = dict(Counter([i.major for i in Document.objects.all()]))
        # domain = dict(Counter([i.domain for i in Document.objects.all()]))

        return render_to_response('stats.html', {'docs':docs,
                                                 'progress': [doc_ann, doc_ann_percent,
                                                              doc_check, doc_check_percent],
                                                 'sents':sents,
                                                 'words':words,
                                                 'annot':annotations,
                                                 'gender':gender,
                                                 'genres':genres,
                                                 # 'course': course,
                                                 # 'major': major,
                                                 # 'domain': domain
                                                 },
                                  context_instance=RequestContext(request))
# todo write login \ registration (if needed??)

class DownloadSearch(Index):

    def get(self, request, page):  # page does nothing here, just ignore it
        if len(request.GET) < 1:
            # QueryFormset = formset_factory(QueryForm, extra=2)
            return render_to_response('download_search.html',
                                      context_instance=RequestContext(request))
        else:
            # print request.GET
            # u_groups = request.user.groups
            query = request.GET
            subcorpus, subcorpus_sents, subcorpus_words, flag = get_subcorpus(query)  # , u_groups)
            # print subcorpus.count()
            # subcorpus_sents = [sent.id for doc in subcorpus[0] for sent in doc.sentence_set.all()]
            count_data = {'total_docs': Document.objects.count(),
                          'total_sents': Sentence.objects.count(),
                          'total_tokens': Token.objects.count(),
                          'subcorpus_docs': len(subcorpus),
                          'subcorpus_sents': subcorpus_sents,
                          'subcorpus_words': subcorpus_words}
            per_page = int(query.get(u'per_page'))
            page = request.GET.get('page')
            page = int(page) if page else 1
            expand = int(query.get(u'expand')[-1])
            sents = []
            if query["exact_word"] != '':
                jq, sent_list, word, res_docs, res_num = exact_search(request.GET["exact_word"].lower().encode('utf-8'),
                                                                      subcorpus, flag, expand, page, per_page)
                sents += sent_list
            else:
                jq, sent_list, word, res_docs, res_num = lex_search(query, subcorpus, flag, expand, page, per_page)
                sents += sent_list
            page += 1
            while page <= math.ceil(float(res_num) / per_page):
                if query["exact_word"] != '':
                    jq, sent_list, word, res_docs, res_num = exact_search(
                        request.GET["exact_word"].lower().encode('utf-8'),
                        subcorpus, flag, expand, page, per_page)
                    sents += sent_list
                else:
                    jq, sent_list, word, res_docs, res_num = lex_search(query, subcorpus, flag, expand, page, per_page)
                    sents += sent_list
                page += 1

            rows = []
            rows.append(
                [u'Номер примера', u'Название текста', u'Оригинальное предложение',
                 u'Тег', u'Ошибка', u'Исправление', u'Комментарий', u'Разметчик'])
            for ind, sent in enumerate(sents):
                anns = Sentence.get_annotations(sent.id)
                if not anns:
                    rows.append([(page - 1) * per_page + 1 + ind, sent.doc_id.title,
                                 reSpan.sub('\\2', sent.tagged).replace('<b>', '{{').replace('</b>', '}}'),
                                 '', '', '', '', ''])
                else:
                    for an in anns:
                        rows.append([(page - 1) * per_page + 1 + ind, sent.doc_id.title,
                                     reSpan.sub('\\2', sent.tagged).replace('<b>', '{{').replace('</b>', '}}'),
                                     an['tag'], an['quote'], an['corr'], an['comment'], an['owner']])

            output = StringIO.StringIO()

            book = xlsxwriter.Workbook(output)
            sheet = book.add_worksheet()
            for row_num, row in enumerate(rows):
                for col_num, item in enumerate(row):
                    sheet.write(row_num, col_num, item)
            book.close()

            # construct response
            output.seek(0)
            response = HttpResponse(output.read(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = 'attachment; filename="results.xlsx"'
            return response
#
# def download(request, page):
#     if len(request.GET) < 1:
#         # QueryFormset = formset_factory(QueryForm, extra=2)
#         return render_to_response('search.html',
#                                   context_instance=RequestContext(request))
#     else:
#         query = request.GET
#         subcorpus, subcorpus_sents, subcorpus_words, flag = get_subcorpus(query)
#         # print subcorpus.count()
#         # subcorpus_sents = [sent.id for doc in subcorpus[0] for sent in doc.sentence_set.all()]
#         count_data = {'total_docs': Document.objects.count(),
#                       'total_sents': Sentence.objects.count(),
#                       'total_tokens': Token.objects.count(),
#                       'subcorpus_docs': len(subcorpus),
#                       'subcorpus_sents': subcorpus_sents,
#                       'subcorpus_words': subcorpus_words}
#         per_page = int(query.get(u'per_page'))
#         page = request.GET.get('page')
#         page = int(page) if page else 1
#         expand = int(query.get(u'expand')[-1])
#         sents = []
#         if query["exact_word"] != '':
#             jq, sent_list, word, res_docs, res_num = exact_search(request.GET["exact_word"].lower().encode('utf-8'),
#                                                                   subcorpus, flag, expand, page, per_page)
#             sents += sent_list
#         else:
#             jq, sent_list, word, res_docs, res_num = lex_search(query, subcorpus, flag, expand, page, per_page)
#             sents += sent_list
#         page += 1
#         while page <= math.ceil(float(res_num) / per_page):
#             if query["exact_word"] != '':
#                 jq, sent_list, word, res_docs, res_num = exact_search(request.GET["exact_word"].lower().encode('utf-8'),
#                                                                       subcorpus, flag, expand, page, per_page)
#                 sents += sent_list
#             else:
#                 jq, sent_list, word, res_docs, res_num = lex_search(query, subcorpus, flag, expand, page, per_page)
#                 sents += sent_list
#             page += 1
#
#         db = Database()
#
#         ids = [int(sent.id) for sent in sents]
#         sentences = []
#         additional = []
#         for i in ids:
#             req = 'SELECT TEXT FROM `annotator_sentence` WHERE id =' + str(i)
#             sentences += [db.execute(req)[0][0]]
#             req2 = 'SELECT data FROM `annotator_annotation` WHERE document_id =' + str(i)
#             additional.append(db.execute(req2))
#
#         docs = [sent.doc_id for sent in sents]
#
#         words = [re.findall('><b>([^><]+?)</b></span>', sent.tagged) for sent in sents]
#
#         l = 0
#         text = u'Имя документа\tПредложение\tРезультат запроса\tФрагменты с тегом\tИсправление\tКомментарий\tТеги\tАвтор тега\n'
#
#         for a in additional:
#             data = []
#             data_q = []
#             for el in a:
#                 j = json.loads(el[0])
#                 try:
#                     data.append(''.join(j['quote']) + '\t' + ''.join(j['text']) + '\t' + ''.join(j['corrs']) + '\t' + ''.join(j['tags']) + '\t' + ''.join(j['owner']))
#                 except:
#                     data.append(''.join(j['quote']) + '\t' + ''.join(j['text']) + '\t\t' + ''.join(j['tags']) + '\t' + ''.join(j['owner']))
#                 data_q.append(''.join(j['quote']))
#             words_l = [re.sub('[— ,.;:!?»«]', '', w) for w in words[l]]
#
#             tagged = []
#             for el in data_q:
#                 bow = ''
#                 if ' ' in el:
#                     splitted = el.split()
#                     if set(words_l) & set(splitted):
#                         bow = el
#                 else:
#                     if el in words_l:
#                         bow = el
#                 tagged.append(bow)
#
#             data_str = ''
#             for t in tagged:
#                 if t == '':
#                     pass
#                 else:
#                     i = data_q.index(t)
#                     data_str += data[i] + '\t'
#             text += ''.join(docs[l].title) + '\t' + sentences[l] + '\t' + ' '.join(words_l) + '\t' + ''.join(data_str) + '\n'
#
#             l += 1
#
#         response = HttpResponse(text, content_type='text/csv; charset="utf-8"')
#         response['Content-Disposition'] = 'attachment; filename="tags.csv"'
#         return response
#
#     # проблема с words_l (не ищутся словосочетания): нужно сделать через старт/энд -> понять, что это значит
#
#
#
