# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Article(models.Model):
    owner = models.ForeignKey(User, db_index=True, blank=True, null=True)
    date = models.DateField(help_text=_("Please use the calendar view to choose date."),verbose_name=_('date'))
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    text_rus = models.TextField(help_text=_("Please enter the news text in Russian."), verbose_name=_('text in Russian'))
    text_eng = models.TextField(help_text=_("Please enter the news text in English."), verbose_name=_('text in English'))

    def __unicode__(self):
        return self.text_eng

    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')
