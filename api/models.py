# from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager


class CustomUser(AbstractUser):
    spent = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(default='/static/421-4212341_default-avatar-svg-hd-png-download.png')

    def __str__(self):
        return f'Name: {self.username} id: {self.id} spent: {self.spent}uah'


class CinemaHall(models.Model):
    hall_name = models.CharField(max_length=255)
    hall_size = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Hall name: {self.hall_name}'


class MovieSeance(models.Model):
    movie_title = models.CharField(max_length=255)
    show_hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='movies')
    start_time_seance = models.TimeField(blank=True, null=True)
    end_time_seance = models.TimeField(blank=True, null=True)
    show_start_date = models.DateTimeField(blank=True, null=True)
    show_end_date = models.DateTimeField(blank=True, null=True)
    free_seats = models.PositiveSmallIntegerField(default=0)
    price = models.SmallIntegerField(default=0)
    image = models.ImageField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    tag = TaggableManager()
    description = RichTextUploadingField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['is_active', 'show_start_date', 'start_time_seance']

    def __str__(self):
        return f'Movie: {self.movie_title} | Price: {self.price} ' \
               f'| Start seance: {self.start_time_seance} | Start date {self.show_start_date.date()}' \
               f'| image: {self.image}'

    def save(self, **kwargs):
        if not self.id:
            self.free_seats = self.show_hall.hall_size
        if not self.slug:
            self.slug = '_'.join(self.movie_title.split())
        return super().save(**kwargs)


class Buying(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchases_user')
    movie = models.ForeignKey(MovieSeance, on_delete=models.CASCADE, related_name='purchases_movie')
    qnt = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'Movie: {self.movie} | Qnt: {self.qnt} | Spent: {self.user.spent}'


class Contacts(models.Model):
    name_cont = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    topic = models.CharField(max_length=100)
    message = models.CharField(max_length=1000)
    time_to_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cont name: {self.name_cont} | Topic: {self.topic}'
