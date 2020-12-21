from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
# requires login before editing or deleting item
from django.contrib.auth.decorators import login_required
# Import models database to use in search
from .models import Product, Category
from django.db.models.functions import Lower
from .forms import ProductForm


# Create your views here.
def all_products(request):
    """ A view to return all products and product search """
    products = Product.objects.all()
    query = None
    categories = None
    sort= None
    direction = None

    if request.GET:

        # if 'sort' in request.GET:
        #     sortkey = request.GET['sort']
        #     if sortkey == "price":
        #         products = products.order_by('-price').reverse()

        # if 'sort' in request.GET:
        #     sortkey = request.GET['sort']
        #     if sortkey == "rating":
        #         products = products.order_by('-rating')

        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            # Returns a list
            # categories = list(request.GET['category'].split(','))
            # Convert into list to compare below
            categories = request.GET['category'].split(',')
            # __name__: Looking for name field in category model since related by foreign key
            # category is present in products field but with number reference, this method allows us to use the actual name
            # instead of number by referencing the category model using foreign key in models.
            # using filter since object already queried
            # category_name obtained from foreignkey defined in Product model/lookups that span relationships
            # Obtaining query set for html(category__name: double undrscore since refering to foeignkey)
            # https://docs.djangoproject.com/en/3.1/topics/db/queries/#lookups-that-span-relationships
            # The __in refers to list. Returns all products with categories in category list as queryset
            # https://docs.djangoproject.com/en/3.1/topics/db/queries/#the-pk-lookup-shortcut
            products = products.filter(category__name__in=categories)
            # Get all categories where name in catgories list as a queryset
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            # Query is blank query= ""
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            else:
                queries = Q(name__icontains=query) | Q(description__icontains=query)
                products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
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


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        # This is a new product, no need to use instance
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # This is the new saved product
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    # Get request
    else:
        form = ProductForm()
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
        
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        # This will get data from form and to update the product instance called above
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        # populate the form with product instance
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))
