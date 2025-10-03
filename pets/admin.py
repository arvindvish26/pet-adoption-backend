from django.contrib import admin
from .models import Pet

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'breed', 'age', 'vaccinated', 'city', 'status')
    search_fields = ('name', 'breed', 'city')
    list_filter = ('status', 'vaccinated', 'city')
