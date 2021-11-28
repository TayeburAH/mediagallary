from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'show_created']


@admin.register(MediaImage)
class MediaImageAdmin(admin.ModelAdmin):
    list_display = ['__str__',]