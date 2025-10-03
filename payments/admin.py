from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'payment_method', 'status', 'amount', 'paid_at')
    list_filter = ('payment_method', 'status')
    search_fields = ('order__id',)
    ordering = ('-paid_at',)
