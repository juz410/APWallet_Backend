import stripe
from app.config import settings

stripe.api_key = settings.stripe_api_key

def create_payment_intent(amount, receipt_email):
    payment_method="pm_card_visa"
    currency="myr"

    resp = stripe.PaymentIntent.create(amount=amount, currency=currency, 
                                       receipt_email=receipt_email ,
                                       payment_method=payment_method)
    resp.confirm()
    return resp