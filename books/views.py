import json
import urllib.request

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from books.forms import BookForm
from books.models import Book


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'


class BookCreateView(LoginRequiredMixin, generic.FormView):
    form_class = BookForm
    template_name = 'books/book_create.html'
    success_url = reverse_lazy('books:book_list')

    def form_valid(self, form):
        key = form.cleaned_data.get('key')

        with urllib.request.urlopen(url=f'https://www.googleapis.com/books/v1/volumes?q={key}') as r:
            result = r.read().decode('UTF-8')
            data = json.loads(result)

        if data.get('totalItems') == 0:
            return messages.error(self.request, 'Book not found with given title.')

        item = data.get('items')[0].get('volumeInfo')

        title = item.get('title')
        author = ', '.join(item.get('authors'))
        published_date = item.get('publishedDate', 0)[:4]
        page_count = item.get('pageCount', 0)
        cover_url = item.get('imageLinks').get('thumbnail')
        language = item.get('language')

        for i in item.get('industryIdentifiers'):
            if i['type'] == 'ISBN_13':
                isbn = i['identifier']
                break
            elif i['type'] == 'ISBN_10':
                isbn = i['identifier']
            else:
                isbn = ''

        Book.objects.create(title=title, author=author, published_date=published_date, isbn=isbn, page_count=page_count,
                            cover_url=cover_url, language=language)

        return super().form_valid(form)
