from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Employer, Candidate, Job, application


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'username',
        'email',
        'role',
        'phone',
        'is_verified',
        'is_active',
    )

    list_filter = (
        'role',
        'is_verified',
        'is_active',
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Zecpath User Information', {
            'fields': (
                'phone',
                'role',
                'is_verified',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'phone',
                'role',
                'is_verified',
                'password1',
                'password2',
            ),
        }),
    )


admin.site.register(Employer)
admin.site.register(Candidate)
admin.site.register(Job)
admin.site.register(application)