from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

class EmailChangeTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.profile.email_confirmed)
        )

email_change_token = EmailChangeTokenGenerator()