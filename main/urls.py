from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('booking/', views.booking_create_view, name='booking_create'),
]
