import random

from django.conf import settings
from authentication.models import Profile
from africastalking.AfricasTalkingGateway import (AfricasTalkingGateway,
                                                 AfricasTalkingGatewayException)

from .models import UserCode

gateway = AfricasTalkingGateway(settings.AFRICASTALKING_USERNAME,
                                settings.AFRICASTALKING_API_KEY)


def generate_code():
    """Generate random 4 digits."""
    return str(random.randrange(100000, 999999))


def send_sms_code(phone_number):
    """Send SMS to new signup to verify."""
    profile = Profile.objects.get(phone_number=phone_number)
    if profile:
        print(profile.user)
        try:
            sms_code = generate_code()
            results = gateway.sendMessage(phone_number, sms_code)
            if results[0]['status'] == 'Success':
                user_code = UserCode(user=profile.user, code=sms_code)
                user_code.save()
        except AfricasTalkingGatewayException as err:
            print(err)
