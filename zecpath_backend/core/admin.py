from django.contrib import admin
from .models import User, Job, application

admin.site.register(User)
admin.site.register(Job)
admin.site.register(application)
# Register your models here.
