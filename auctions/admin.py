from django.contrib import admin
from .models import User, Bid, Category, Listing

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Listing)