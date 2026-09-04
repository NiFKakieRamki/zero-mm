from django.contrib import admin
from .models import ProcedureType
from .models import Zone
from .models import Service

admin.site.register(ProcedureType)
admin.site.register(Zone)
admin.site.register(Service)
