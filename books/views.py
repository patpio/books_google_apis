from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from books.models import Book


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'


class BookCreateView(LoginRequiredMixin, generic.CreateView):
    model = Book
    fields = ['title']
    template_name = 'books/book_create.html'
