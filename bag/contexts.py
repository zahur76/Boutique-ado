from decimal import Decimal
from django.conf import settings
from products.models import Product
from django.shortcuts import get_object_or_404
# By using contexts.py the context will be be available across all apps
# Must be added into templates in settings file


def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})
    # bag = {'1': 2, '2': 1, '3': {'item_by_size': {'m': 1, 'l': 2}}, '4': {'item_by_size': {'xl': 1}}}
    for item_id, item_data in bag.items():
        # if dictionary does not have size:
        if isinstance(item_data, int):
            product = get_object_or_404(Product, pk=item_id)
            total += item_data * product.price
            product_count += item_data
            sub_total = item_data*product.price
            bag_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
                'sub_total': sub_total,
            })
        # if item_data is a dictionary
        else:
            product = get_object_or_404(Product, pk=item_id)
            # item_data = bag[item_id]
            for size, quantity in bag[item_id]['items_by_size'].items():
                total += quantity * product.price
                product_count += quantity
                sub_total = quantity*product.price
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'size': size,
                    'sub_total': sub_total,
                })

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0
    
    sub_total = quantity*product.price
    grand_total = delivery + total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context
