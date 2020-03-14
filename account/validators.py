from django.core.validators import MinLengthValidator,MaxLengthValidator


class SignUpMaxLengthValidator(MaxLengthValidator):
    message = "რა იყო არაბი ხარ ბლიად? სიგრძე მაქსიმუმ %(limit_value)d სიმბოლოსგან უნდა შედგებოდეს." \
              " (შეყვანილია %(show_value)d სიმბოლო)"