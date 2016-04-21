__author__ = 'elmira'

from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

class QueryForm(forms.Form):
    wordform = forms.CharField(max_length=100)
    lex = forms.CharField(max_length=100)
    grams = forms.CharField(max_length=100)
    errors = forms.CharField(max_length=100)
    additional = forms.CharField(max_length=100)
    distance_from = forms.IntegerField()
    to = forms.IntegerField()