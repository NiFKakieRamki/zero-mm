from django.contrib import admin
from .models import ProcedureType
from .models import Zone
from .models import Service, Booking, Profile, WorkSettings, TimeOff
from django.utils.html import format_html

admin.site.site_header = '0 миллиметров'
admin.site.site_title = '0 миллиметров'
admin.site.index_title = 'Управление сайтом'

admin.site.register(ProcedureType)
admin.site.register(Zone)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user__username', 'phone', 'notes')
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'is_showcased')
    list_filter = ('procedure_type', 'zone', 'is_active', 'is_showcased')
    search_fields = ('procedure_type__name', 'zone__name')
    list_editable = ('is_showcased',)

@admin.register(WorkSettings)
class WorkSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'work_starts', 'work_ends', 'min_hours_before_visit', 'slot_step_minutes')
    fieldsets = (
        ('Рабочие дни', {
            'description': 'Отмеченные дни — рабочие',
            'fields': (('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'),),
        }),
        ('Рабочее время', {
            'fields': (('work_starts', 'work_ends'),),
        }),

        ('Запись', {
            'fields': ('min_hours_before_visit', 'slot_step_minutes'),
        }),
    )
    

    def has_add_permission(self, request):
        if WorkSettings.objects.exists():
            return False
        return True


@admin.register(TimeOff)
class TimeOffAdmin(admin.ModelAdmin):
    list_display = ('starts_at', 'ends_at', 'comment')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('starts_at', 'client__username', 'client__first_name', 'client__profile__phone', 'total_duration_minutes', 'total_price', 'colored_status', 'created_at')
    list_filter = ('status',)
    date_hierarchy = 'starts_at'
    filter_horizontal = ('services',)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.update_total()

    def changelist_view(self, request, extra_context=None):
        Booking.mark_finished()
        return super().changelist_view(request, extra_context)

    @admin.display(description='Статус', ordering='status')
    def colored_status(self, obj):
        colors = {
            Booking.Status.PLANNED: '#15803d',
            Booking.Status.DONE: '#6b7280',
            Booking.Status.CANCELLED: '#b91c1c',
            Booking.Status.NO_SHOW: '#c2410c',
        }
        return format_html('<b style="color: {}">{}</b>', colors[obj.status], obj.get_status_display())

