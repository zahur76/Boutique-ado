from django.http import HttpResponse

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

import json
import time

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        # This is pid created by intent
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info
        # This comes from intent.charges succeded
        billing_details = intent.charges.data[0].billing_details
        # This gets the shipping data from intent dictionary
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Clean data in the shipping details/Since null in model
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            # This was sent to webhook to be saved via metadata
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()

        # Method3
        attempt = 1
        order = False
        while order is False and attempt <= 5:
            try:
                order = Order.objects.get(stripe_pid=pid)
                order = True
                break
            # Remember when using except must use Model name Order and not order
            except Order.DoesNotExist:
                order = False
                attempt += 1
                time.sleep(1)
                print(attempt)
        if order is True:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
            # This implies sumbit button has not been activated
        else:
            print('Order not in model')
            order = None
            try:
                # Need to create Object since not using form
                order = Order.objects.create(
                    full_name=shipping_details.name,                    
                    user_profile=profile,
                    # Present in billing address only/Needed for search in model
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
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
            # For any reason cannot create object
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        return HttpResponse(
            # Will show in stripe / as if page was closed after pressing submit button
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

        # # Check if order exists in model method 2
        # order = Order.objects.filter(stripe_pid='kk').exists()
        # attempt = 1
        # order = False
        # while order is False and attempt <= 5:
        #     order
        #     print(order)
        #     attempt += 1
        #     time.sleep(1)
        #     print(attempt)         

        # if order is True:
        #     return HttpResponse(
        #         content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
        #         status=200)
        #     # This implies sumbit button has not been activated
        # else:
        #     print('Order not in model')
        #     try:
        #         # Need to create Object since not using form
        #         order = Order.objects.create(
        #             full_name=shipping_details.name,
        #             # Present in billing address only/Needed for search in model
        #             email=billing_details.email,
        #             phone_number=shipping_details.phone,
        #             country=shipping_details.address.country,
        #             postcode=shipping_details.address.postal_code,
        #             town_or_city=shipping_details.address.city,
        #             street_address1=shipping_details.address.line1,
        #             street_address2=shipping_details.address.line2,
        #             county=shipping_details.address.state,
        #             original_bag=bag,
        #             stripe_pid=pid,
        #         )
        #         for item_id, item_data in json.loads(bag).items():
        #             product = Product.objects.get(id=item_id)
        #             if isinstance(item_data, int):
        #                 order_line_item = OrderLineItem(
        #                     order=order,
        #                     product=product,
        #                     quantity=item_data,
        #                 )
        #                 order_line_item.save()
        #             else:
        #                 for size, quantity in item_data['items_by_size'].items():
        #                     order_line_item = OrderLineItem(
        #                         order=order,
        #                         product=product,
        #                         quantity=quantity,
        #                         product_size=size,
        #                     )
        #                     order_line_item.save()
        #     # For any reason cannot create object
        #     except Exception as e:
        #         if order:
        #             order.delete()
        #         return HttpResponse(
        #             content=f'Webhook received: {event["type"]} | ERROR: {e}',
        #             status=500)
        # return HttpResponse(
        #     # Will show in stripe / as if page was closed after pressing submit button
        #     content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
        #     status=200)

        # order_exists = False
        # attempt = 1
        # while attempt <= 5:
        #     try:
        #         order = Order.objects.get(
        #             full_name__iexact=shipping_details.name,
        #             email__iexact=billing_details.email,
        #             phone_number__iexact=shipping_details.phone,
        #             country__iexact=shipping_details.address.country,
        #             postcode__iexact=shipping_details.address.postal_code,
        #             town_or_city__iexact=shipping_details.address.city,
        #             street_address1__iexact=shipping_details.address.line1,
        #             street_address2__iexact=shipping_details.address.line2,
        #             county__iexact=shipping_details.address.state,
        #             grand_total=grand_total,
        #             original_bag=bag,
        #             stripe_pid=pid,
        #         )
        #         order_exists = True
        #         break
        #     except Order.DoesNotExist:
        #         attempt += 1
        #         time.sleep(1)
        # if order_exists:
        #     return HttpResponse(
        #         content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
        #         status=200)
        # else:
        #     order = None
        #     try:
        #         # Need to create model since not using form
        #         order = Order.objects.create(
        #             full_name=shipping_details.name,
        #             # Present in billing address only/Needed for search in model
        #             email=billing_details.email,
        #             phone_number=shipping_details.phone,
        #             country=shipping_details.address.country,
        #             postcode=shipping_details.address.postal_code,
        #             town_or_city=shipping_details.address.city,
        #             street_address1=shipping_details.address.line1,
        #             street_address2=shipping_details.address.line2,
        #             county=shipping_details.address.state,
        #             original_bag=bag,
        #             stripe_pid=pid,
        #         )
        #         for item_id, item_data in json.loads(bag).items():
        #             product = Product.objects.get(id=item_id)
        #             if isinstance(item_data, int):
        #                 order_line_item = OrderLineItem(
        #                     order=order,
        #                     product=product,
        #                     quantity=item_data,
        #                 )
        #                 order_line_item.save()
        #             else:
        #                 for size, quantity in item_data['items_by_size'].items():
        #                     order_line_item = OrderLineItem(
        #                         order=order,
        #                         product=product,
        #                         quantity=quantity,
        #                         product_size=size,
        #                     )
        #                     order_line_item.save()
        #     except Exception as e:
        #         if order:
        #             order.delete()
        #         return HttpResponse(
        #             content=f'Webhook received: {event["type"]} | ERROR: {e}',
        #             status=500)
        # return HttpResponse(
        #     # Will show in stripe / as if page was closed after pressing submit button
        #     content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
        #     status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)