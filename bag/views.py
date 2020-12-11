from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product


# Create your views here.
def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    if request.POST:
        product = get_object_or_404(Product, pk=item_id)
        quantity = int(request.POST.get('quantity'))
        # Requesting the current URL by obtaining value of request.path
        redirect_url = request.POST.get('redirect_url')
        size = None
        # Search a session dictionary called bag or if doesnt exist will create one
        # if bag:
        # bag = bag
        # else:
        # bag = {}
        bag = request.session.get('bag', {})
        # Have to specify if since not all products have size
        if 'product_size' in request.POST:
            # Always request name to obtain value
            size = request.POST['product_size']
            # bag = {'1': 2, '2': 1, '3':{"item_by_size": {'m':1, 'l':2} }}
            # print(bag)
            # size= 'xl'
            # item_id = '4'
            # if item_id in bag.keys():
            # if size in bag[item_id]['item_by_size'].keys():
            #     bag[item_id]['item_by_size'][size] += 1
            # else:
            #     bag[item_id]['item_by_size'][size] = 1
            # else:
            # bag[item_id] = {'item_by_size': {size: 1}}
            # print(bag)
            # if item exists in bag
            if item_id in bag.keys():
                # If item size already exists
                if size in bag[item_id]['items_by_size'].keys():
                    bag[item_id]['items_by_size'][size] += quantity
                    messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
                else:
                    bag[item_id]['items_by_size'][size] = quantity
                    messages.success(request, f'Added {size.upper()} {product.name} to your bag')
                # If item size does not exist
            else:
                # create field in dictionary
                # bag['4'] = {'item_by_size':{'xl': 2}}
                bag[item_id] = {'items_by_size': {size: quantity}}
                messages.success(request, f'Added {size.upper()} {product.name} to your bag')
        else:
            # same as: if item_id in bag
            # bag = {'jeans': 2, 'shirts': 3, 'trousers': 5}
            # item = 'panties'
            # if item in bag:
            # bag[item] += 1
            # else:
            # bag[item] = 1
            if item_id in bag.keys():
                bag[item_id] += quantity
                messages.success(request, f'Updtaed {product.name} quantity to {bag[item_id]}')
            else:
                bag[item_id] = quantity
                messages.success(request, f'Added {product.name} to your bag')

        # This will overwrite session with new dictionary/ must be in reverse
        request.session['bag'] = bag
        print(bag)
        return redirect(redirect_url)


def adjust_bag(request, item_id):
    """ Adjust quantity of the specified product in shopping bag """
    if request.POST:
        product = get_object_or_404(Product, pk=item_id)
        quantity = int(request.POST.get('quantity'))
        size = None
        bag = request.session.get('bag', {})
        # Have to specify if since not all products have size
        if 'product_size' in request.POST:
            # Always request name to obtain value
            size = request.POST['product_size']
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')

        else:
            bag[item_id] = quantity
            messages.success(request, f'Updated {product.name} quantity {bag[item_id]}')
        # This will overwrite session with new dictionary/ must be in reverse
        request.session['bag'] = bag
        return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""
    product = get_object_or_404(Product, pk=item_id)
    try:
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag')

        if size:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
                messages.success(request, f'Removed {size.upper()} {product.name} from bag')
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from bag')

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
