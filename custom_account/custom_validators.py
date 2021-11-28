from django.core.validators import ValidationError
from validate_email import validate_email
import re


# pip install py3-validate-email

def validate_your_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.search(regex, email)):
        raise ValidationError('Email is invalid!')
    if not validate_email(email):
        raise ValidationError('Invalid Email. Please provide a valid email.')
    else:
        return email


'''
dns: domain name system
The main function of DNS is to translate domain names into IP Addresses,
which browsers use to load internet pages
'''
