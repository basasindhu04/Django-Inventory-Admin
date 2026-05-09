from django.contrib import admin
from django.utils.html import format_html
from django.db import transaction
from django.contrib import messages
from django.urls import path
from django.shortcuts import render
from django.db.models import F, Sum
from .models import Product, StockAudit

class StockAuditInline(admin.TabularInline):
    model = StockAudit
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [StockAuditInline]
    list_display = ('name', 'sku', 'price', 'stock', 'category', 'stock_status_badge')
    list_editable = ('stock',)
    list_filter = ('category',)
    search_fields = ('name', 'sku')

    def stock_status_badge(self, obj):
        if obj.stock < 10:
            return format_html('<span style="color: red;">Low Stock</span>')
        elif 10 <= obj.stock <= 50:
            return format_html('<span style="color: orange;">Acceptable</span>')
        else:
            return format_html('<span style="color: green;">Good</span>')
    
    stock_status_badge.short_description = 'Stock Status'

    @admin.action(description='Mark selected products for clearance (50% off)')
    def mark_clearance(self, request, queryset):
        try:
            with transaction.atomic():
                for product in queryset:
                    original_price = product.price
                    product.price *= 0.5
                    product.save()

                    StockAudit.objects.create(
                        product=product,
                        delta=0,
                        reason='Price marked for clearance',
                        performed_by=request.user
                    )
            self.message_user(request, f'{queryset.count()} products were successfully marked for clearance.', messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f'An error occurred: {e}', messages.ERROR)

    actions = [mark_clearance]

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'profile'):
            return obj.category == request.user.profile.managed_category
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='inventory-dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        total_value_agg = Product.objects.aggregate(
            total_value=Sum(F('price') * F('stock'))
        )
        total_value = total_value_agg.get('total_value', 0) or 0

        low_stock_products = Product.objects.filter(stock__lt=10).order_by('stock')[:5]

        context = dict(
           self.admin_site.each_context(request),
           total_value=total_value,
           low_stock_products=low_stock_products,
        )
        return render(request, "admin/inventory/dashboard.html", context)

@admin.register(StockAudit)
class StockAuditAdmin(admin.ModelAdmin):
    list_display = ('product', 'delta', 'reason', 'performed_by', 'created_at')
