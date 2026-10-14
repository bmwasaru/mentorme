from django.conf import settings

from celery import shared_task
from celery.utils.log import get_task_logger

from authentication.models import UserCode
from authentication.tokens import generate_random_code

import africastalking

# Specify your login credentials
username = settings.AFRICAS_TALKING_USERNAME
api_key = settings.AFRICAS_TALKING_API_KEY

logger = get_task_logger(__name__)


@shared_task(name='send_verification_code_sms')
def send_verification_code_sms(user):
    """Sends Verification Code SMS"""
    logger.info("Sends Verification Code SMS")
    code = generate_random_code()
    message = "Your verification code is {0}".format(code)
    africastalking.initialize(username, api_key)
    results = africastalking.SMS.send(message, [user.profile.phone_number])
    recipients = results.get('SMSMessageData', {}).get('Recipients', [])
    if recipients and all(recipient.get('statusCode') in (100, 101, 102)
                          for recipient in recipients):
        UserCode.objects.update_or_create(user=user, defaults={'code': code})
