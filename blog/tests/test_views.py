from django.test import TestCase

from blog.models import Author
from django.urls import reverse


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создает 12 авторов для пагинации.
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(
                first_name = 'Christian %s' % author_num,
                last_name = 'Surname %s' % author_num,
                )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/blog/authors/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'blog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        # Получает вторую страницу и подтверждает, что на ней осталось ровно 3 элемента
        resp = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['author_list']) == 3)



import datetime
from django.utils import timezone

from blog.models import BookInstance, Book, Genre, Language
from django.contrib.auth.models import User  # для представления User как borrower


class LoanedBookInstancesByUserListViewTest(TestCase):
    
    def setUp(self):
        # Создает двух пользователей
        test_user1 = User.objects.create_user(username='testuser1', password='lhbnoFdb49')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='Jnsvnd549e')
        test_user2.save()

        # Создает книги
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language
            )
        
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Присвоение типов many-to-many напрямую недоступно
        test_book.save()


        # Создает 30 объектов BookInstance
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy%5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status
                )

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(resp, '/accounts/login/?next=/blog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='lhbnoFdb49')
        resp = self.client.get(reverse('my-borrowed'))

        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Проверка ответ на запрос
        self.assertEqual(resp.status_code, 200)
        # Проверка, что мы используем правлильный шаблон
        self.assertTemplateUsed(resp, 'blog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='lhbnoFdb49')
        resp = self.client.get(reverse('my-borrowed'))

        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Проверка, что мы получаем успешный ответ
        self.assertEqual(resp.status_code, 200)

        # Проверка, что изначально у нас нет книг в списке
        self.assertTrue('bookinstance_list' in resp.context)
        self.assertEqual(len(resp.context['bookinstance_list']), 0)

        # Проверка, что все книги "взяты на прокат"
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status='o'
            copy.save()

        # Проверка, что все забронированные книги в списке
        resp = self.client.get(reverse('my-borrowed'))
        # Проверка, что пользователь залогинилс
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Проверка успешности ответа
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('bookinstance_list' in resp.context)

        # Подтверждение, что все книги принадлежат testuser1 и взяты "на прокат"
        for bookitem in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):
        
        # Изменение стфтуса "в прокате"
        for copy in BookInstance.objects.all():
            copy.status='o'
            copy.save()

        login = self.client.login(username='testuser1', password='lhbnoFdb49')
        resp = self.client.get(reverse('my-borrowed'))

        # Проверка, что пользователь залогинилс
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Проверка успешности ответа
        self.assertEqual(resp.status_code, 200)

        # Проверка, что из всего списка показывается только 10 экземпляров
        self.assertEqual(len(resp.context['bookinstance_list']), 10)

        last_date = 0
        for copy in resp.context['bookinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)



from django.contrib.auth.models import Permission  #Требуется необходимый доступ, чтобы установить книгу как "возвращенную"


class RenewBookInstancesViewTest(TestCase):

    def setUp(self):
        # Создает пользователя
        test_user1 = User.objects.create_user(username='testuser1', password='lhbnoFdb49')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='Jnsvnd549e')
        test_user2.save()
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Создание книги
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language
            )
        # Создание жанра Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Создание объекта BookInstance для test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(book=test_book,
                                                            imprint='Unlikely Imprint, 2016', 
                                                            due_back=return_date,
                                                            borrower=test_user1, status='o')

        # Создание объекта BookInstance для test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(book=test_book, 
                                                            imprint='Unlikely Imprint, 2016',
                                                            due_back=return_date, 
                                                            borrower=test_user2, 
                                                            status='o')

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk}))
        # Вручную проверить перенаправление (assertRedirect невозможно использовать, поскольку URL-адрес перенаправления непредсказуем)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='lhbnoFdb49')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance2.pk}))
        # Чтобы удедиться, что у нас есть доступ в систему и есть соответствующее разрешение.
        self.assertEqual(resp.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
        # Чтобы убедиться, что у  нас есть доступ в систему. Статус staff, поэтому можем просматривать все книги.
        self.assertEqual(resp.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4() # маловероятно, что UID совпадет с нашим bookinstance
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':test_uid,}))
        self.assertEqual(resp.status_code, 404)

    def test_user_correct_template(self):
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
        self.assertEqual(resp.status_code, 200)
        # Проверка, что мы используем правильный шаблон.
        self.assertTemplateUsed(resp, 'blog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}) )
        self.assertEqual(resp.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':valid_date_in_future} )
        self.assertRedirects(resp, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':date_in_past} )
        self.assertEqual( resp.status_code,200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':invalid_date_in_future} )
        self.assertEqual( resp.status_code,200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')


class AuthorCreateViewTest(TestCase):
    """Тест представления AuthorCreate."""
    def setUp(self):
        # Создание пользователя
        test_user1 = User.objects.create_user(username='testuser1', password='lhbnoFdb49')
        test_user2 = User.objects.create_user(username='testuser2', password='Jnsvnd549e')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Создание книги
        test_author = Author.objects.create(first_name='John', last_name='Smith')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author-create'))
        self.assertRedirects(response, '/accounts/login/?next=/blog/author/create/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='lhbnoFdb49')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)

    def test_user_correct_template(self):
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/author_form.html')

    def test_redirects_to_detail_view_on_success(self):
        login = self.client.login(username='testuser2', password='Jnsvnd549e')
        response = self.client.post(reverse('author-create'), {'first_name': 'Christian Name', 'last_name': 'Surname'})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/blog/author/'))
        