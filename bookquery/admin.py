from django.contrib import admin

from .models import BookQuery, DownloadCount

admin.site.register(BookQuery)
admin.site.register(DownloadCount)

# Register your models here.
