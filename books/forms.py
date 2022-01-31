from django import forms


class BookForm(forms.Form):
    key = forms.CharField()
