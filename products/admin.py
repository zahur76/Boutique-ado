from django.contrib import admin
from .models import Product, Category

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    # what to be displayed in admin
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )
    # How we wish to order in admin
    ordering = ('sku',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

# The model followed by class name (model, class name)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
