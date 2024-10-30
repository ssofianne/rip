from django.contrib import admin
from .models import Work, Reconstruction, Space

class ReconstructionAdmin(admin.ModelAdmin):
    readonly_fields = ('fundraising',)

admin.site.register(Work)
admin.site.register(Reconstruction, ReconstructionAdmin)
admin.site.register(Space)

