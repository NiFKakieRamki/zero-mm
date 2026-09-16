from datetime import datetime, timedelta
from django.utils import timezone
from .models import WorkSettings, Booking, TimeOff

def get_slots(day, duration_minutes):
    work_settings = WorkSettings.get_settings()

    working_days = [work_settings.monday, work_settings.tuesday, work_settings.wednesday, work_settings.thursday, work_settings.friday, work_settings.saturday, work_settings.sunday]

    if working_days[day.weekday()] == False:
        return []

    day_start = timezone.make_aware(datetime.combine(day, work_settings.work_starts))
    day_ends = timezone.make_aware(datetime.combine(day, work_settings.work_ends))

    duration = timedelta(minutes=duration_minutes)
    step = timedelta(minutes=work_settings.slot_step_minutes)
    min_booking_time = timezone.now() + timedelta(hours=work_settings.min_hours_before_visit)

    day_bookings = Booking.objects.filter(starts_at__date=day, status=Booking.Status.PLANNED)
    day_time_offs = TimeOff.objects.filter(starts_at__lt=day_ends, ends_at__gt=day_start)

    slots = []
    slot_start = day_start

    while slot_start + duration <= day_ends:
        slot_end = slot_start + duration
        available = True

        if slot_start < min_booking_time:
            available = False

        for booking in day_bookings:
            booking_ends_at = booking.starts_at + timedelta(minutes=booking.total_duration_minutes)
            if slot_start < booking_ends_at and slot_end > booking.starts_at:
                available = False

        for time_off in day_time_offs:
            if slot_start < time_off.ends_at and slot_end > time_off.starts_at:
                available = False

        slots.append({'time': f'{slot_start:%H:%M}', 'available': available})
        slot_start += step

    return slots