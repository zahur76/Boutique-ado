from django.db import models


class Category(models.Model):

    class Meta:
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    # Will return the actual name in admin fields
    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    # null=True will set empty values in the database
    # blank=True, value is not required
    # Adds category to product model and allows query of category from product model
    # id field automatically assigned
    # Product can only have 1 category so place foreign key here
    # If request for product: product.category. If reverse then category.product.all()
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL) # related_name ='prod'
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    has_sizes = models.BooleanField(default=False, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
