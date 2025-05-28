from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing_page/<int:id>", views.listing_page, name='listing_page'),
    path("place_bid/<int:id>", views.place_bid, name='place_bid'),
    path("categories", views.all_categories, name='all_categories'),
    path("categoty_list/<int:id>", views.category_list, name='category_list'),
]
