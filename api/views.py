import json
from datetime import timedelta

import taggit
from django.core.mail import send_mail
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from taggit.models import Tag

from api.filters import MyTimeRangeAndHallFilter
from api.serializers import CinemaHallSerializer, MovieSeanceSerializer, BuyingSerializer, \
    CustomUserSerializer, ContactSerailizer, TagSerializer
from api.models import CinemaHall, MovieSeance, Buying, CustomUser


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_query_param = 'page_size'
    max_page_size = 10


class ProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get(self, request, *args,  **kwargs):
        return Response({
            "user": CustomUserSerializer(request.user, context=self.get_serializer_context()).data,
        })


class CustomUserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ['post', ]
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (AllowAny, )
        return super().get_permissions()

    def get_serializer_context(self):
        data_from_postman = self.request.data.pop('str_data', False)
        if data_from_postman:
            json_data = json.loads(*data_from_postman)
            self.request.data.update(json_data)
        return super().get_serializer_context()


class CinemaHallViewSet(ModelViewSet):
    queryset = CinemaHall.objects.all()
    serializer_class = CinemaHallSerializer
    permission_classes = [IsAdminUser]
    # pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny, )
        return super().get_permissions()
    
    def get_queryset(self):
        a = 1
        return super(CinemaHallViewSet, self).get_queryset()


class MovieSeanceViewSet(ModelViewSet):
    queryset = MovieSeance.objects.filter(show_end_date__gt=timezone.now())
    serializer_class = MovieSeanceSerializer
    permission_classes = [IsAdminUser]
    # filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_backends = [SearchFilter]
    ordering_fields = ['price', 'start_time_seance', ]
    # filter_class = MyTimeRangeAndHallFilter
    pagination_class = CustomPagination
    lookup_field = 'slug'
    search_fields = ["movie_title"]
    
    def get_serializer_context(self):
        data_from_postman = self.request.data.pop('str_data', False)
        if data_from_postman:
            json_data = json.loads(*data_from_postman)
            self.request.data.update(json_data)
        return super().get_serializer_context()

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_queryset(self):
        dtn = timezone.now()
        td = timedelta(days=1)
        show_day = self.kwargs.get('show_day', False)

        if show_day == 'today':
            return super().get_queryset().filter(show_start_date__lte=dtn, show_end_date__gt=dtn)
        elif show_day == 'tomorrow':
            return super().get_queryset().filter(show_start_date__lte=dtn + td, show_end_date__gt=dtn + td)
        return super().get_queryset()


class BuyingViewSet(ModelViewSet):
    queryset = Buying.objects.all()
    serializer_class = BuyingSerializer
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    lookup_field = 'slug'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).order_by('-id')


class TagDetailView(ListAPIView):
    queryset = MovieSeance.objects.all()
    serializer_class = MovieSeanceSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        try:
            tag_slug = self.kwargs['tag_slug'].lower()
            tag = Tag.objects.get(slug=tag_slug)
            return super().get_queryset().filter(tag=tag)
        except taggit.models.Tag.DoesNotExist:
            return super(TagDetailView, self).get_queryset()


class TagView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class FeedBackView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ContactSerailizer

    def post(self, request, *args, **kwargs):
        serializer_class = ContactSerailizer(data=request.data)
        if serializer_class.is_valid():
            data = serializer_class.validated_data
            name = data.get('name')
            from_email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            send_mail(f'От {name} | {subject}', message, from_email, ['dimakozhurin28@gmail.com'])
            return Response({"success": "Sent"})
        return Response("Form is not valid!")


class LastFiveMoviesView(ListAPIView):
    queryset = MovieSeance.objects.all().order_by('-id')[:5]
    serializer_class = MovieSeanceSerializer
    permission_classes = [AllowAny]
