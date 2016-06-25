from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display      = [ 'picture','user_name', 'user_email','user_password','height_field','width_field']
    search_fields     = ('picture','user_name', 'user_email')


    def user_name(self, obj):
        return obj.user.username

    def user_password(self, obj):
        return obj.user.password

    def user_email(self, obj):
        return obj.user.email

admin.site.register(UserProfile, UserProfileAdmin)
