from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from .models import Service, Booking
from .forms import BookingForm, RegisterForm
from datetime import date
from django.http import JsonResponse
from .slots import get_slots


def home_view(request):
    services = (
        Service.objects
        .filter(is_showcased=True, is_active=True)
        .select_related('procedure_type', 'zone')
        )
    return render(request, 'home.html', {'showcased': services})


def register_view(request):
    if request.method =='POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            new_user = form.save()
            new_user.profile.phone = form.cleaned_data['phone']
            new_user.profile.save()
            login(request, new_user)

            return redirect('main:home')

    else:
        form = RegisterForm()

    return render(request, 'main/register.html', {'form': form})


@login_required
def booking_create_view(request):
    
    selected_service_ids = []

    if request.method == 'POST':
        form = BookingForm(request.POST)

        for value in request.POST.getlist('services'):
            selected_service_ids.append(int(value))

        if form.is_valid():
            new_booking = form.save(commit=False)
            new_booking.client = request.user
            new_booking.save()
            form.save_m2m()
            new_booking.update_total()

            messages.success(request, f'Вы успешно записались к мастеру. Дата записи: {new_booking.starts_at:%d.%m.%Y %H:%M}. Стоимость — {new_booking.total_price} ₽')

            return redirect('main:home')


    else:
        form = BookingForm()

    services = (
        Service.objects
        .filter(is_active=True)
        .select_related('procedure_type', 'zone')
        .order_by('procedure_type__name', 'zone__name')
    )

    grouped = defaultdict(list)
    for service in services:
        grouped[service.procedure_type].append(service)

    context = {
        'form': form,
        'service_groups': list(grouped.items()),
        'selected_service_ids': selected_service_ids
    }


    return render(request, 'booking_form.html', context)


def login_view(request):
    if request.method =='POST':
        form = AuthenticationForm(request, data=request.POST)
        next_url = request.POST.get('next')

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('main:home')

    else:
        form = AuthenticationForm()

    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    logout(request)

    return redirect('main:home')

@login_required
def booking_slot_view(request):
    date_str = request.GET.get('date')
    duration_str = request.GET.get('duration')

    if not date_str or not duration_str or not duration_str.isdigit():
        return JsonResponse({'slots': []})

    try:
        day = date.fromisoformat(date_str)

    except ValueError:
        return JsonResponse({'slots': []})

    slots = get_slots(day, int(duration_str))

    return JsonResponse({'slots': slots})

    
@login_required
def my_bookings_view(request):
    Booking.mark_finished()

    bookings = Booking.objects.filter(client=request.user).prefetch_related('services').order_by('-starts_at')

    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required
def booking_cancel_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, client=request.user)

    if request.method == 'POST':
        if booking.status == Booking.Status.PLANNED and booking.starts_at > timezone.now():
            booking.status = Booking.Status.CANCELLED
            booking.save()
            messages.success(request, 'Запись отменена')
        else:
            messages.error(request, 'Эту запись уже нельзя отменить')

    return redirect('main:my_bookings')
