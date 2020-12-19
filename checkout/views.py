from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from bag.contexts import bag_contents

import stripe
import json


@require_POST
def cache_checkout_data(request):
    # This is done since following info cannot be sent in stripe.confirmCardPayment
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # To obtain information from form to send to model
    # Post will only work once stripe has checked card details
    if request.method == 'POST':

        bag = request.session.get('bag', {})
        # Get all info from form/This is the Order Model
        # form_data = {
        #     'full_name': request.POST['full_name'],
        #     'email': request.POST['email'],
        #     'phone_number': request.POST['phone_number'],
        #     'country': request.POST['country'],
        #     'postcode': request.POST['postcode'],
        #     'town_or_city': request.POST['town_or_city'],
        #     'street_address1': request.POST['street_address1'],
        #     'street_address2': request.POST['street_address2'],
        #     'county': request.POST['county'],
        # }
        # Make instance of form filled with form data
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            # https://docs.djangoproject.com/en/3.1/topics/forms/modelforms/
            # save form to model Order
            # This method creates and saves a database object from the data bound to the form, ie Order
            # small letter order represents the Order model
            # Commit=False prevents saving since still have addional fields to enter into model not present in form
            # We are saving to the attached Object model
            order = order_form.save(commit=False)
            # same as intent.id/included in form
            pid = request.POST.get('client_secret').split('_secret')[0]
            # We are saving to the order Object model created above fields which are not present in form and are present in model
            # The Object belonging to the Order model is called order
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        # Save info to OrderLineItem/ This requires Order plus other fields as per model
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        # Save to OrderLineItem model
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # Must use Product not product when raising exceptions
                # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#methods-that-do-not-return-querysets
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))
            # saving save-info value/checked or not checked
            request.session['save_info'] = 'save-info' in request.POST
            # Order has been saved above and repesents the Order model
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    # Get request when havent submitted form yet and checkout page loads
    else:
        # If no items in bag
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))
        # Get the bag content from bag context.py so as to get the 'grand_total'
        else:
            current_bag = bag_contents(request)
            # Obtaining values from another view(context bag_content)
            # This is get request and will make a payment intent to stripe when page loads
            total = current_bag['grand_total']
            stripe_total = round(total * 100)
            # Required to make request for intent.client_secret/Payment intent
            stripe.api_key = stripe_secret_key
            # Create intent/Returns a dictionary
            # https://stripe.com/docs/payments/payment-intents#creating-a-paymentintent
            intent = stripe.PaymentIntent.create(
                amount=stripe_total,
                currency=settings.STRIPE_CURRENCY,
            )
            # intent.client_secret: pi_1HzFW6L9RkpyhrRPmehv8jxK_secret_FThAHTXI6pCMZqusFdMiNf7Zy
            # Make instance of order form to be used in checkout.html
            print(intent.client_secret)
            print(intent.id)
            # Creates Order model from form/Prefill form if user profile exists
            if request.user.is_authenticated:
                try:
                    profile = UserProfile.objects.get(user=request.user)
                    order_form = OrderForm(initial={
                        'full_name': profile.user.get_full_name(),
                        'email': profile.user.email,
                        'phone_number': profile.default_phone_number,
                        'country': profile.default_country,
                        'postcode': profile.default_postcode,
                        'town_or_city': profile.default_town_or_city,
                        'street_address1': profile.default_street_address1,
                        'street_address2': profile.default_street_address2,
                        'county': profile.default_county,
                    })
                except UserProfile.DoesNotExist:
                    order_form = OrderForm()
            else:
                order_form = OrderForm()
            

    # Public key sent to template to used by JS
    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        # Created by stripe when intent is made/ When we go to checkout page
        'client_secret': intent.client_secret,
    }
    return render(request, template, context)


def checkout_success(request, order_number):
    # If Checkout success page loads this means the checkout was successful
    # and Order has been created stored in database
    # Order does not have field user_profile yet
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    # Order has been saved in model above
    order = get_object_or_404(Order, order_number=order_number)

    # https://docs.djangoproject.com/en/3.1/topics/auth/default/#authentication-in-web-requests
    # Checks to see if user is logged in
    if request.user.is_authenticated:
        # Will obtain Userprofile for current user
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        # https://docs.djangoproject.com/en/3.1/ref/models/instances/#updating-attributes-based-on-existing-fields
        # Save the user_profile field in Order model requested above
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            # Obtains data from the Order we created so it can be updated in userprofile
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            # https://docs.djangoproject.com/en/3.1/topics/forms/modelforms/#the-save-method
            # Here we are updating an exisitng model, hence we use instance.
            # Instance is equal to the Model profile we want to update and profile_data the data
            # Make instance of Userprofile form
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            # prefer to use form since we can validate
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)
