import datetime as dt

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User


class AbstractCategoryGenre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        abstract = True


class Category(AbstractCategoryGenre):
    """Категории произведений"""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('id',)


class Genre(AbstractCategoryGenre):
    """Жанры произведений"""

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('id',)


class Title(models.Model):
    """Произведения"""
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    year = models.IntegerField(
        verbose_name='Год издания',
        validators=(MaxValueValidator(int(dt.datetime.now().year)),)
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанры'
    )
    description = models.TextField(
        null=True,
        verbose_name='Описание'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return f'{self.name}'


class GenreTitle(models.Model):
    """Связи моделей жанра и произведения"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.title} относится к жанру {self.genre}'


class Review(models.Model):
    """Отзывы на произведения."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    score = models.PositiveIntegerField(
        verbose_name="Оценка",
        validators=(
            MinValueValidator(
                1, message='Значение меньше минимального.'
                'Значение должно быть от 1 до 10'
            ),
            MaxValueValidator(
                10, message='Значение больше максимального.'
                'Значение должно быть от 1 до 10'
            ),
        )
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review',
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Комментарии на отзывы."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
