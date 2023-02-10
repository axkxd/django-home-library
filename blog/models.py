from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date

import uuid


class Genre(models.Model):
    '''Модель, представляющая книжный жанр.'''
    name = models.CharField(max_length=200, help_text='Укажите жанр книги (например: научная фантастика)')

    def __str__(self):
        '''Строка для представления объекта Model.'''
        return self.name


class Language(models.Model):
    """Модель, представляющая язык (например, английский, французский, японский и т.д.)"""
    name = models.CharField(max_length=200,
                            help_text='Введите оригинальный язык книги (например: английский, французкий, японский и т.д.')

    def __str__(self):
        """Строка для представления объекта модели (на сайте администратора и т. д.)"""
        return self.name


class Book(models.Model):
    """Модель, представляющая книгу (но не конкретный экземпляр книги)."""
    title = models.CharField(max_length=200)

    # Используется внешний ключ (ForeignKey), потому что у книги может быть только один автор, а у авторов может быть несколько книг
    # Author - это строка, а не объект, потому что он еще не объявлен в файле
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text='Введите краткое описание книги')
    isbn = models.CharField('ISBN', max_length=13, unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    # Используется ManyToManyField, поскольку жанр может содержать много книг. Книги могут охватывать множество жанров.
    # Класс Genre уже определен, поэтому мы можем указать объект выше.
    genre = models.ManyToManyField(Genre, help_text='Выберите жанр для этой книги')

    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['title', 'author']

    def display_genre(self):
        """Создайте строку для Жанра. Это необходимо для отображения жанра в Admin."""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        '''Возвращает URL-адрес для доступа к подробной записи для этой книги.'''
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        '''Строка для представления объекта модели.'''
        return self.title


class BookInstance(models.Model):
    """Модель, представляющая определенный экземпляр книги 
    (т.е. который можно взять в библиотеке)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Уникальный идентификатор этой конкретной книги во всей библиотеке')
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        """Определяет, является ли книга просроченной, на основе даты выполнения и текущей даты."""
        return bool(self.due_back and date.today() > self.due_back)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """Строка для представления объекта модели."""
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """Модель, представляющая автора."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Возвращает URL-адрес для доступа к конкретному экземпляру автора."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """Строка для представления объекта модели."""
        return f'{self.last_name}, {self.first_name}'