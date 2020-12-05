from django.shortcuts import render, redirect


# Create your views here.
def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    if request.POST:
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
            # print(bag['3']['item_by_size'].keys())
            # if 'xl' in bag['3']['item_by_size'].keys():
            # bag['3']['item_by_size']['m']+=1
            # else:
            # bag['3']['item_by_size']['xl'] = 1
            # print(bag)
            if item_id in bag.keys():
                # item already exists but size already present
                if size in bag[item_id]['items_by_size'].keys():
                    bag[item_id]['items_by_size'][size] += quantity
                # item already exists but slected size not present, it will create field
                else:
                    bag[item_id]['items_by_size'][size] = quantity
            else:
                # create field in dictionary
                # bag['4'] = {'item_by_size':{'xl': 2}}
                bag[item_id] = {'items_by_size': {size: quantity}}
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
            else:
                bag[item_id] = quantity

        # This will overwrite session with new dictionary/ must be in reverse
        request.session['bag'] = bag

        return redirect(redirect_url)
