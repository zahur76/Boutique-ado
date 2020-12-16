from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler

import stripe


@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Will return a event
    # Setup
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    # Set up a webhook handler/Make instance of stripewh_handler
    handler = StripeWH_Handler(request)
    # class calculator:
    # def add(a,b):
    #     return a+b

    # cals = calculator

    # print(cals.add(2,2))

    # Map webhook events to relevant handler functions in webhook handler
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }
    # Get the webhook type from Stripe
    # Event returns a dictionary
    # {
    # "created": 1326853478,
    # "livemode": false,
    # "id": "evt_00000000000000",
    # "type": "invoice.updated",
    # }
    event_type = event['type']
    # If there's a handler for it, get it from the event map
    if event_type in event_map:
        event_handler = event_map[event_type]
    # Use the generic one by default
    else:
        event_handler = handler.handle_event
    # Call the event handler with the event from webhook handler
    response = event_handler(event)
    return response
