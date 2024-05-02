from django.contrib import admin
from .forms import *

# Register your models here.
from .models import *


class SaveProduct(admin.ModelAdmin):
    list_display = ['code', 'category_id', 'name', 'description', 'price', 'date_added', 'date_updated', 'status']
    form = SaveProduct
    list_filter = ['name', 'category_id', 'status']
    search_fields = ['category_id', 'name', 'date_added', 'date_updated', 'status']


class StockHistorySearch(admin.ModelAdmin):
    list_display = ['id', 'item_ID', 'category', 'item_name', 'quantity', 'issue_quantity', 'receive_quantity',
                    'issue_by', 'receive_by', 'last_updated']
    form = StockHistorySearchForm
    list_filter = ['item_ID', 'category']
    search_fields = ['category', 'item_name', 'start_date', 'end_date']

#admin.site.register(Stock, StockCreateAdmin)
admin.site.register(Category)
admin.site.register(Orders)
admin.site.register(Products)
admin.site.register(StockHistory, StockHistorySearch)
admin.site.register(Sales)
admin.site.register(SalesItems)
admin.site.register(Supplier)
admin.site.register(Purchases)