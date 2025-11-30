from django.urls import path
from .import views

urlpatterns = [
path("", views.index, name="" ),
path("register", views.register_page, name="register" ),
path("my-login", views.my_login, name="my-login" ),
]
