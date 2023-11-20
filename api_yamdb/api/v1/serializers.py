"""Сериализаторы приложения API."""

from django.shortcuts import get_object_or_404
from django.core.validators import RegexValidator

from rest_framework import serializers

from core.data_hash import hash_sha256
from users.models import User
from reviews.models import Category, Comment, Genre, Review, Title


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                r'^[-a-zA-Z0-9_]+$',
                message='Поле не соответсвует требованиям.',
                code='invalid_username',
            )
        ],
    )
    email = serializers.EmailField(max_length=254, required=True)

    def validate_username(self, value):
        """Метод для валидации username."""

        if value == 'me':
            raise serializers.ValidationError(
                {'username': 'Никнейм "me" запрещен.'},
            )
        return value


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        user = get_object_or_404(User, username=username)
        if hash_sha256(confirmation_code) != user.confirmation_code:
            raise serializers.ValidationError({
                'confirmation_code': 'Неверный код подтверждения.'
            })
        return data


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для операций с моделью User."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_username(self, value):
        """Метод для валидации username."""

        if value == 'me':
            raise serializers.ValidationError(
                {'username': 'Никнейм "me" запрещен.'},
            )

        return value


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для показа произведений."""
    category = CategorySerializer(many=False)
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'category',
            'genre',
            'rating'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведений."""
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'category',
            'genre',
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ревью."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = ("id", "author", "review", "text", "pub_date")
        read_only_fields = ("review",)
        model = Comment
