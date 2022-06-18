from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import CinemaHallViewSet, MovieSeanceViewSet, BuyingViewSet, \
    CustomUserViewSet, TagDetailView, FeedBackView, TagView, LastFiveMoviesView, ProfileView

router = routers.SimpleRouter()
router.register(r'cinema_halls', CinemaHallViewSet)
router.register(r'movie_seances', MovieSeanceViewSet)
router.register(r'buying', BuyingViewSet)
router.register(r'users', CustomUserViewSet)
router.register(r'registration', CustomUserViewSet)
urlpatterns = [
    path("tags/<slug:tag_slug>/", TagDetailView.as_view()),
    path("tags/", TagView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("last_five/", LastFiveMoviesView.as_view()),
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("refresh_token/", TokenRefreshView.as_view(), name="refresh_token"),
    path("feedback/", FeedBackView.as_view()),
    path("ckeditor/", include('ckeditor_uploader.urls')),
              ] + router.urls
