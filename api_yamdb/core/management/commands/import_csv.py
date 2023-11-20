import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from progress.bar import IncrementalBar
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User


def category_create(row):
    Category.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2],
    )


def genre_create(row):
    Genre.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2],
    )


def titles_create(row):
    Title.objects.get_or_create(
        id=row[0],
        name=row[1],
        year=row[2],
        category_id=row[3],
    )


def review_create(row):
    title, _ = Title.objects.get_or_create(id=row[1])
    Review.objects.get_or_create(
        id=row[0],
        title=title,
        text=row[2],
        author_id=row[3],
        score=row[4],
        pub_date=row[5]
    )


def comment_create(row):
    review, _ = Review.objects.get_or_create(id=row[1])
    Comment.objects.get_or_create(
        id=row[0],
        review=review,
        text=row[2],
        author_id=row[3],
        pub_date=row[4],
    )


def genre_title_create(row):
    title, _ = Title.objects.get_or_create(id=row[1])
    genre, _ = Genre.objects.get_or_create(id=row[2])
    GenreTitle.objects.get_or_create(
        id=row[0],
        title=title,
        genre=genre,
    )


def users_create(row):
    User.objects.get_or_create(
        id=row[0],
        username=row[1],
        email=row[2],
        role=row[3],
        bio=row[4],
        first_name=row[5],
        last_name=row[6]
    )


action = {
    'category.csv': category_create,
    'genre.csv': genre_create,
    'titles.csv': titles_create,
    'users.csv': users_create,
    'review.csv': review_create,
    'comments.csv': comment_create,
    'genre_title.csv': genre_title_create
}


class Command(BaseCommand):
    """Команда для загрузки csv файлов в базу данных."""
    def handle(self, *args, **options):
        for filename, row in action.items():
            path = os.path.join(settings.BASE_DIR, "static/data/") + filename
            with open(path, 'r', encoding='utf-8') as file:
                row_count = sum(1 for row in file)
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                bar = IncrementalBar(filename.ljust(17), max=row_count)
                next(reader)
                for row in reader:
                    bar.next()
                    action[filename](row)
                bar.finish()
        self.stdout.write("___The files were uploaded successfully___")
