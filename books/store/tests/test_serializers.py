from django.contrib.auth.models import User
from django.db.models import Count, When, Avg
from django.test import TestCase
from pycparser.c_ast import Case

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        user3 = User.objects.create(username='user3')

        book1 = Book.objects.create(name='Test book 1', price=25,
                                    author_name='Author 1')
        book2 = Book.objects.create(name='Test book 2', price=35,
                                    author_name='Author 2')

        UserBookRelation.objects.create(user=user1, book=book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=book1, like=True, rate=4)

        UserBookRelation.objects.create(user=user1, book=book2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=book2, like=True, rate=4)
        UserBookRelation.objects.create(user=user3, book=book2, like=False, rate=5)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate')
        ).order_by('id')
        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': book1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Author 1',
                'likes_count': 3,
                'annotated_likes': 3,
                'rating': '4.67'
            },
            {
                'id': book2.id,
                'name': 'Test book 2',
                'price': '35.00',
                'author_name': 'Author 2',
                'likes_count': 2,
                'annotated_likes': 2,
                'rating': '3.50'
            },
        ]
        print(data)
        self.assertEqual(expected_data, data)