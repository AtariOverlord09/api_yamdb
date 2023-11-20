"""Обработчики приложения API."""
from uuid import uuid4 as uid

from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import (
    DjangoFilterBackend,
)
from rest_framework.exceptions import ValidationError
from rest_framework import (
    generics,
    status,
    viewsets,
    permissions,
    serializers,
    filters,
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from core.pagination import PageNumPagination
from .serializers import (
    SignupSerializer,
    TokenObtainSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleRetrieveSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    UsersSerializer,
    CommentSerializer,
)
from .permissions import (
    AdminOnlyPermission,
    AdminOrReadOnlyPermission,
    IsAuthorModeratorAdminOrReadOnly
)
from users.models import User
from reviews.models import Genre, Category, Title, Review
from .filters import TitleFilter
from .mixins import GenreCategoryMixin
from core.send_mail import send_mail
from core.data_hash import hash_sha256


class GenreViewSet(GenreCategoryMixin):
    """Вьюсет жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(GenreCategoryMixin):
    """Вьюсет категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет произведений"""
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    )
    permission_classes = (
        AdminOrReadOnlyPermission,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleRetrieveSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly,)
    pagination_class = PageNumPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        user = self.request.user
        title = self.get_title()
        if Review.objects.filter(author=user, title=title):
            raise ValidationError('Ваш отзыв на это произведение уже есть')
        serializer.save(author=user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly, )

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class SignupView(generics.CreateAPIView):
    """Обработчик для регистрации пользователей."""
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        token = User._meta.get_field('confirmation_code').max_length
        confirmation_code = str(uid().int)[:token]
        try:
            user, created = User.objects.get_or_create(
                username=username,
                email=email,
            )
        except IntegrityError:
            raise serializers.ValidationError({
                'error': ('Пользователь с таким email или username уже '
                          'существует.')
            })

        user.confirmation_code = hash_sha256(confirmation_code)
        send_mail(
            from_email='yam.db.bot@support.com',
            to_email=email,
            subject='Confiramtion Code',
            message=f'Your confirmation code: {confirmation_code}',
        )
        user.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class TokenObtainView(generics.GenericAPIView):
    """Обработчик для получения токена по коду подтверждения."""
    serializer_class = TokenObtainSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data.get('username'),
        )
        user.is_active = True
        token = RefreshToken.for_user(user)
        user.confirmation_code = ''
        user.save()
        return Response(
            {'token': str(token.access_token), },
            status=status.HTTP_200_OK,
        )


class UsersViewSet(viewsets.ModelViewSet):
    """Обработчик для модели User."""
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (
        permissions.IsAuthenticated,
        AdminOnlyPermission,
    )

    @action(
        methods=('GET', 'PATCH'),
        detail=False,
        url_path='me',
        permission_classes=(permissions.IsAuthenticated, ),
    )
    def self_user(self, request):
        """Метод для взаимодействия с собственным аккаунтом."""

        user = User.objects.get(username=request.user.username)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data)
