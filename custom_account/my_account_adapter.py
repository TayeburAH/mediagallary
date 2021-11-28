from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.signals import pre_social_login
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from django.shortcuts import resolve_url, redirect
from django.contrib import messages
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponseRedirect
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import authenticate, login, logout
from allauth.account.admin import EmailAddress
from django.dispatch import receiver

User = get_user_model()


# https://github.com/pennersr/django-allauth/blob/master/allauth/account/adapter.py
class MyAppAccountAdapter(DefaultAccountAdapter):
    def get_logout_redirect_url(self, request):
        pass
        """
        Returns the URL to redirect to after the user logs out. Note that
        this method is also invoked if you attempt to log out while no users
        is logged in. Therefore, request.user is not guaranteed to be an
        authenticated user.
        """
        # return redirect('login_process')

    # Stopping Auto login when social media_mediagallery authenticated
    def login(self, request, user):
        if not request.user.is_authenticated:
            print(type(user))  # <class 'custom_account.models.User'>
            if user is not None:
                login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
                pass

                # add the backend to the function
            else:
                messages.error(request, 'Login not successful')


# https://github.com/pennersr/django-allauth/blob/master/allauth/socialaccount/adapter.py
class MyAppSocialAccountAdapter(DefaultSocialAccountAdapter):
    # login(request, user) Before we did this
    @transaction.atomic
    def pre_social_login(self, request, sociallogin):
        print('1')
        # social account i.e facebook account/google account in their server exists , if so, no need to do anything
        # Auto login will happen
        if sociallogin.is_existing:
            print('sociallogin exits so return none')
            return

        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        if 'email' not in sociallogin.account.extra_data:
            print('no email so return none')
            return
        # Any account made from social media_mediagallery is_customer and is_active true
        # find the first verified email that we get from this sociallogin
        # verified_email = None
        # for email in sociallogin.email_addresses:
        #     if email.verified:
        #         verified_email = email
        #         break

        # if social account does not exist, it creates one by default


@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    print('2')
    # raise in try/except prints whatever in ''
    try:
        user = User.objects.get(email=sociallogin.email_addresses[0])
        if not user.is_active:
            # Login
            # send OTP
            if not request.user.is_authenticated:
                print(type(user))  # <class 'custom_account.models.User'>
                if user is not None:
                    login(request, user, backend='custom_account.backends.EmailOrPhoneModelBackend')
                    raise Exception("send_otp")  # purposely raise error
        # This user now can be authenticated without password through google or facebook
        sociallogin.connect(request, user)  # goes to def login(self, request, user):
        print('Did not log in')
    except Exception as e:
        if str(e) == 'send_otp':
            raise ImmediateHttpResponse(redirect('send_otp'))

        if str(e) == 'User matching query does not exist.':
            return

        print(e)
        messages.info(request, 'Login failed, try again')
        raise ImmediateHttpResponse(redirect('login_process'))  # send it back to login if anything goes wrong

    # To show which social media_mediagallery authenticated the user
    request.session['provider'] = None
    request.session['provider'] = sociallogin.account.provider.capitalize()
    messages.info(request, f'You are authenticated by {sociallogin.account.provider.capitalize()}')

    # user = User.objects.get(email=sociallogin.email_addresses[0])
    # sociallogin.connect(request, user)

# <--------- Notes ------------>
# storage = messages.get_messages(request)
# for message in storage:
#     pass
# storage.used = True
# print(list(messages.get_messages(request)))
#
#
# print(sociallogin.user)  # Blank
# print(sociallogin.user.email)  # Gives the email from provider
# print(sociallogin.user.email == 'tayebur@canadaeducationbd.com')
# print(sociallogin.account.extra_data['email'])
# print(sociallogin.is_existing) # True or False
# print(sociallogin.user.id)     #  26, gives the Id if it was saved before

# Remove the messages that come automatically
# \venv\Lib\site-packages\allauth\templates\account\messages\logged_in.txt
