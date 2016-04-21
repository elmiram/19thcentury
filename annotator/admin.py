from django.contrib import admin
from annotator.models import Document, Annotation, Sentence, Token, Morphology
from news.models import Article
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

class CorpusAdminSite(AdminSite):
    site_header = '19th Century Corpus'
    site_title = 'Admin'
    index_title = 'Texts'

class ArticleAdmin(admin.ModelAdmin):
    fields = ['date', 'text_eng', 'text_rus']
    list_display = ('date', 'text_eng', 'text_rus', 'created')

class DocumentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['owner', 'body', 'filename']}),
        ('Author', {'fields': [('author', 'gender')]}),
        ('Date', {'fields': [('date1')]}),
        ('Text', {'fields': [('genre')]}),
        ('Autocompletion', {'fields': [('annotated', 'checked', 'title')], 'classes': [('collapse')]}),
    ]

    list_display = ('title', 'author', 'gender',  'date_displayed', 'words', 'created', 'annotated', 'checked')
    list_filter = ['gender', 'annotated', 'checked', 'genre']


class AnnotationAdmin(admin.ModelAdmin):
    readonly_fields = ('annotated_doc',)
    list_display = ('annotated_doc', 'tag', 'owner', 'updated', 'created')

    def annotated_doc(self, instance):
        return instance.document.doc_id.title


class MorphAdmin(admin.ModelAdmin):
    list_display = ('token', 'lem', 'lex', 'gram')


class MorphInline(admin.TabularInline):
    model = Morphology
    extra = 0


class TokenAdmin(admin.ModelAdmin):
    readonly_fields = ('sent_num',)
    fieldsets = [
        (None,               {'fields': ['token', 'doc', 'sent']}),
        ('Token data', {'fields': [('num', 'punctl', 'punctr', 'sent_pos')]}),
    ]

    list_display = ('token', 'sent_num', 'num', 'doc')
    inlines = [MorphInline]

    def sent_num(self, instance):
        return instance.sent.num


learner_admin = CorpusAdminSite(name='admin')
learner_admin.register(Document, DocumentAdmin)
learner_admin.register(Annotation, AnnotationAdmin)
# learner_admin.register(Sentence)
# learner_admin.register(Token, TokenAdmin)
# learner_admin.register(Morphology, MorphAdmin)
learner_admin.register(Article, ArticleAdmin)
learner_admin.register(User, UserAdmin)
learner_admin.register(Group, GroupAdmin)
