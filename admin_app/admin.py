from django.contrib import admin
from django.contrib.auth import get_user_model
from admin_app.models import POD

User = get_user_model()

# Register your models here.
admin.site.register(POD)

# Check if the User model is already registered
if not admin.site.is_registered(User):
    admin.site.register(User)
