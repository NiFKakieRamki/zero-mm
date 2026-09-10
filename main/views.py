from django.shortcuts import render, redirect
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import  AuthenticationForm
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Service
from .forms import BookingForm, RegisterForm


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
    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            new_booking = form.save(commit=False)
            new_booking.client = request.user
            new_booking.save()
            form.save_m2m()
            new_booking.update_total()

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
        'service_groups': list(grouped.items())
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
