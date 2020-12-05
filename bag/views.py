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
        # Search a session dictionary called bag or if doesnt exist will create one
        # if bag:
        # bag = bag
        # else:
        # bag = {}
        bag = request.session.get('bag', {})
        # same as: if item_id in bag
        # bag = {'jeans': 2, 'shirts': 3, 'trousers': 5}
        # item = 'panties'
        # if item in bag:
        # bag[item] += 1
        # else:
        # bag[item] = 1

        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity
        # This will overwrite session with new dictionary
        request.session['bag'] = bag

        return redirect(redirect_url)
