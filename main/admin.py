from django.contrib import admin
from .models import ProcedureType
from .models import Zone
from .models import Service

admin.site.site_header = '0 миллиметров'
admin.site.site_title = '0 миллиметров'
admin.site.index_title = 'Управление сайтом'

admin.site.register(ProcedureType)
admin.site.register(Zone)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'is_showcased')
    list_filter = ('procedure_type', 'zone', 'is_active', 'is_showcased')
    search_fields = ('procedure_type__name', 'zone__name')
    list_editable = ('is_showcased',)


