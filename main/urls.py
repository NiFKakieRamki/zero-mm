from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('booking/', views.booking_create_view, name='booking_create'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('booking/slots/', views.booking_slot_view, name='booking_slots'),
    path('services/', views.services_view, name='services'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('my-bookings/<int:booking_id>/cancel/', views.booking_cancel_view, name='booking_cancel'),
    path('tips/', views.tips_view, name='tips'),
    path('privacy/', views.privacy_view, name='privacy'),

]
