from django import forms


class BookForm(forms.Form):
    key = forms.CharField()


class BookChoiceForm(forms.Form):
    select = forms.ChoiceField(label='Select your book', help_text='Choose only one')
