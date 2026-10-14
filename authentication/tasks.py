from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from celery import shared_task
from celery.utils.log import get_task_logger

from authentication.models import UserCode
from authentication.tokens import generate_random_code

import africastalking

logger = get_task_logger(__name__)


@shared_task(name='send_verification_code_sms')
def send_verification_code_sms(user_id):
    """Sends Verification Code SMS"""
    user = User.objects.select_related('profile').get(pk=user_id)
    if user.is_active or user.profile.role != 'mentee':
        return
    code = generate_random_code()
    UserCode.objects.update_or_create(user=user, defaults={
        'code': make_password(code), 'issued_at': timezone.now(), 'attempts': 0,
    })
    message = "Your verification code is {0}".format(code)
    africastalking.initialize(settings.AFRICAS_TALKING_USERNAME, settings.AFRICAS_TALKING_API_KEY)
    results = africastalking.SMS.send(message, [user.profile.phone_number])
    recipients = results.get('SMSMessageData', {}).get('Recipients', [])
    if not recipients or not all(recipient.get('statusCode') in (100, 101, 102)
                                 for recipient in recipients):
        raise RuntimeError('SMS provider did not accept the verification message.')
