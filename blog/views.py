import datetime

from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from blog.forms import RenewBookForm
from blog.models import Author


def index(request):
    """Функция просмотра главной страницы сайта."""
    #Сгенерировать кол-во некоторых основных объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Доступные книги (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # 'all()' подразумевается по умолчанию
    num_authors = Author.objects.count()

    # Все доступные жанры
    num_gener = Genre.objects.count()

    # Количество посещений этого представления
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_gener': num_gener,
        'num_visits': num_visits,
    }

    # Визуализировать HTML-шаблон index.html с данными в переменной context
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    """Обшее представление списка книг на основе классов."""
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    """Общее представление сведений для книги на основе классов."""
    model = Book


class AuthorListView(generic.ListView):
    """Общее представление списка авторов на основе классов."""
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Общий список книг на основе классов, предоставленных текущему пользователю во временное пользование."""
    model = BookInstance
    template_name = 'blog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user)\
                .filter(status__exact='o').order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Общее представление на основе классов, в котором перечислены все книги, взятые во временное пользование. Видно только пользователям с разрешением can_mark_returned."""
    model = BookInstance
    permission_required = 'blog.can_mark_returned'
    template_name = 'blog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@login_required
@permission_required('blog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """Функция просмотра для обновления конкретного экземпляра BookInstance библиотекарем."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # Обработает данные, если это POST запрос
    if request.method == 'POST':
        # Создает экземпляр формы и заполняет его данными из запроса
        form = RenewBookForm(request.POST)

        if form.is_valid():
            # Обработает данные в form.cleaned_data и запишет их в поле модели due_back
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # Перенапрвляет на новый URL
            return HttpResponseRedirect(reverse('all-borrowed'))
    
    # Если запрос GET (или другой метод), создает форму по умолчанию.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'blog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'blog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'
    permission_required = 'blog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'blog.can_mark_returned'


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'blog.can_mark_returned'
    

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'blog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'blog.can_mark_returned'



from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer, GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    '''
    Конечная точка API, которая позволяет 
    пользователям просматиривать или редактировать.
    '''
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    '''
    Конечная точка API, которая позволяет 
    просматривать или редактировать группы.
    '''
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

