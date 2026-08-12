from django.contrib import admin
from .models import (
    Category, Event, Profile, EventMember,
    Registration, Wishlist, Budget, Notification,
)

admin.site.register(Category)
admin.site.register(Event)
admin.site.register(Profile)
admin.site.register(EventMember)
admin.site.register(Registration)
admin.site.register(Wishlist)
admin.site.register(Budget)
admin.site.register(Notification)
