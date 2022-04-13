from django.contrib import admin

from api.models import CustomUser, CinemaHall, MovieSeance, Buying, Contacts

admin.site.register(CustomUser)
admin.site.register(CinemaHall)
admin.site.register(MovieSeance)
admin.site.register(Buying)
admin.site.register(Contacts)
