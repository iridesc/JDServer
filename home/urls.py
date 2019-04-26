from django.urls import path #引入path
from . import views #引入testapp的views


urlpatterns = [
    path('', views.home,)
]
