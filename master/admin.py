from django.contrib import admin
from .models import Client, WorkService, Assignment, Work, Document

# Register your models here.
admin.site.register(Client)
admin.site.register(WorkService)
admin.site.register(Assignment)
admin.site.register(Work)
admin.site.register(Document)
