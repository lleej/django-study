from django.contrib import admin

# Register your models here.
from . import models

admin.register(models.Place, 'oil')
admin.register(models.Restaurant, 'oil')