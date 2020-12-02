from django.shortcuts import render, get_object_or_404
# Import models database to use in search 
from .models import Product


# Create your views here.
def all_products(request):
    """ A view to return all products and product search """
    products = Product.objects.all()

    context = {
        'products': products,
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to return product a with specific id/pk """
    # Search for product in Product Model using pk identifier obtained from project_id
    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }
    return render(request, 'products/product_detail.html', context)
