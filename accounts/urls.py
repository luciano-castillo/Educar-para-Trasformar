from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login_usuario, name="login"),
    path("logout/", views.logout_usuario, name="logout"),
    path("inicio/", views.inicio_por_rol, name="inicio_por_rol"),
]