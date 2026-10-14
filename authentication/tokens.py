import random

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                str(user.pk) + str(timestamp) +
                str(user.profile.email_confirmed)
        )


account_activation_token = AccountActivationTokenGenerator()


def generate_random_code():
    """Generate 6 digit random code"""
    return str(random.randrange(100000, 999999))
