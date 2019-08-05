from django import forms
from tweet_alert.models import Alert

class AlertForm(forms.Form):
    """
    A form which takes an email address, a set of keywords, and email message settings.
    """

    email = forms.EmailField()

class RegistrationForm(forms.Form):
    """
    A form which takes an email address as the username, and a password.
    """

    email = forms.EmailField()