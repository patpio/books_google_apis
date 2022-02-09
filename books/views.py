import json
import urllib.request

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from books.forms import BookForm, BookChoiceForm
from books.models import Book


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = Book.objects.filter(added_by=self.request.user)
        query = self.request.GET.get('search')

        if query:
            queryset = queryset.filter(author__contains=query)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('search') and not self.queryset:
            context['no_result'] = True

        return context


class BookCreateView(LoginRequiredMixin, generic.FormView):
    template_name = 'books/book_create.html'
    success_url = reverse_lazy('books:book_list')

    def get_form_class(self):
        return BookChoiceForm if self.request.session.get('data') else BookForm

    def get_form(self, *args, **kwargs):
        data = self.request.session.get('data')
        form = super().get_form(*args, **kwargs)
        if data:
            items = []
            for item in data['items']:
                item_vol = item['volumeInfo']
                items.append((item['id'], f"'{item_vol.get('title')}' by {', '.join(item_vol.get('authors', ''))}, year: {item_vol.get('publishedDate')[:4]}"))

            form.fields['select'].choices = items

        return form

    def form_valid(self, form):
        key = form.cleaned_data.get('key', '')

        if key:
            key = key.replace(' ', '_')
            with urllib.request.urlopen(url=f'https://www.googleapis.com/books/v1/volumes?q={key}') as r:
                result = r.read().decode('UTF-8')
                data = json.loads(result)

            if data.get('totalItems') == 0:
                messages.error(self.request, 'Book not found with given title.', extra_tags='danger')
                return redirect(reverse('books:book_create'))

            if data.get('totalItems') > 1:
                self.request.session['data'] = data
                return redirect(reverse('books:book_create'))

            item = data.get('items')[0].get('volumeInfo')

        else:
            data = self.request.session.get('data', {}).get('items')
            self.request.session['data'] = None
            item = [book for book in data if book['id'] == form.cleaned_data.get('select')][0].get('volumeInfo')

        title = item.get('title')
        author = ', '.join(item.get('authors'))
        published_date = item.get('publishedDate', 0)[:4]
        page_count = item.get('pageCount', 0)
        cover_url = item.get('imageLinks', {}).get('thumbnail', '/static/images/placeholder.jpg')
        language = item.get('language')
        added_by = self.request.user

        for i in item.get('industryIdentifiers'):
            if i['type'] == 'ISBN_13':
                isbn = i['identifier']
                break
            elif i['type'] == 'ISBN_10':
                isbn = i['identifier']
            else:
                isbn = ''

        Book.objects.create(title=title, author=author, published_date=published_date, isbn=isbn, page_count=page_count,
                            cover_url=cover_url, language=language, added_by=added_by)

        return super().form_valid(form)
