from django.conf import settings

from celery.task import task
from celery.utils.log import get_task_logger

from authentication.models import UserCode
from authentication.tokens import generate_random_code

from africastalking.AfricasTalkingGateway import (AfricasTalkingGateway, AfricasTalkingGatewayException)

# Specify your login credentials
username = settings.AFRICAS_TALKING_USERNAME
api_key = settings.AFRICAS_TALKING_API_KEY

gateway = AfricasTalkingGateway(username, api_key)

logger = get_task_logger(__name__)


@task(name='send_verification_code_sms')
def send_verification_code_sms(user):
    """Sends Verification Code SMS"""
    logger.info("Sends Verification Code SMS")
    code = generate_random_code()
    message = "Your verification code is {0}".format(code)
    results = gateway.sendMessage(user.profile.phone_number, message)
    if results.status == "success":
        UserCode(user=user, code=code).save()
