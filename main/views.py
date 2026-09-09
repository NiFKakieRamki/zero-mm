from django.shortcuts import render, redirect
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from .models import Service
from .forms import BookingForm


def home_view(request):
    services = (
        Service.objects
        .filter(is_showcased=True, is_active=True)
        .select_related('procedure_type', 'zone')
        )
    return render(request, 'home.html', {'showcased': services})


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




