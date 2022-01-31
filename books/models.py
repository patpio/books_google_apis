from datetime import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    published_date = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year)])
    isbn = models.CharField(max_length=13)
    page_count = models.PositiveIntegerField()
    cover_url = models.URLField()
    language = models.CharField(max_length=20)

    def __str__(self):
        return self.title
