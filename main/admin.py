from django.contrib import admin
from .models import ProcedureType
from .models import Zone
from .models import Service, Booking, Profile

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

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('starts_at', 'client', 'total_duration_minutes', 'total_price', 'status')
    date_hierarchy = 'starts_at'
    filter_horizontal = ('services',)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.update_total()

