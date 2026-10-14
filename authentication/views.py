import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from authentication.forms import SignUpForm, VerificationForm
from authentication.models import UserCode
from authentication.tasks import send_verification_code_sms

logger = logging.getLogger(__name__)
PENDING_USER_SESSION_KEY = 'pending_verification_user'
CODE_LIFETIME = timedelta(minutes=10)
RESEND_INTERVAL = timedelta(seconds=60)
MAX_CODE_ATTEMPTS = 5


def _send_code(request, user):
    try:
        # Deliver before responding, without requiring a running Celery worker.
        send_verification_code_sms(user.pk)
    except Exception:
        logger.warning('Verification SMS delivery failed for user %s', user.pk)
        messages.error(request, 'We could not send your code. Please wait a minute and try sending it again.')
    else:
        messages.success(request, 'A verification code has been sent to your phone.')


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('initial_setup')
    form = SignUpForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data.get('email', ''),
                is_active=False,
            )
            user.profile.role = form.cleaned_data['role']
            user.profile.phone_number = form.cleaned_data.get('phone_number', '')
            user.profile.save()
        if user.profile.role == 'mentor':
            return render(request, 'authentication/pending_approval.html')
        request.session.cycle_key()
        request.session[PENDING_USER_SESSION_KEY] = user.pk
        _send_code(request, user)
        return redirect('verify_account')
    return render(request, 'authentication/signup.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def verify_account(request):
    user = User.objects.filter(
        pk=request.session.get(PENDING_USER_SESSION_KEY),
        is_active=False, profile__role='mentee',
    ).first()
    if user is None:
        request.session.pop(PENDING_USER_SESSION_KEY, None)
        return redirect('signup')
    form = VerificationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and request.POST.get('action') == 'resend':
        code = UserCode.objects.filter(user=user).first()
        if code and timezone.now() - code.issued_at < RESEND_INTERVAL:
            messages.error(request, 'Please wait a minute before requesting another code.')
        else:
            _send_code(request, user)
        return redirect('verify_account')
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            code = UserCode.objects.select_for_update().filter(user=user).first()
            if code is None or timezone.now() - code.issued_at >= CODE_LIFETIME:
                form.add_error('code', 'This code has expired. Request a new code.')
            elif code.attempts >= MAX_CODE_ATTEMPTS:
                form.add_error('code', 'Too many incorrect attempts. Request a new code.')
            elif not check_password(form.cleaned_data['code'], code.code):
                code.attempts += 1
                code.save(update_fields=['attempts'])
                form.add_error('code', 'The verification code is incorrect.')
            else:
                user.is_active = True
                user.save(update_fields=['is_active'])
                code.delete()
                request.session.pop(PENDING_USER_SESSION_KEY, None)
                messages.success(request, 'Your phone number is verified. You can now log in.')
                return redirect('login')
    return render(request, 'authentication/verify_account.html', {'form': form})
