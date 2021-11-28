import shutil
import os

from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.signals import pre_social_login
from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete, pre_delete
from django.dispatch import receiver
from allauth.account.admin import EmailAddress
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from .models import *
from django.core.files.storage import default_storage as storage
import cloudinary.uploader
from django.contrib.auth import authenticate, login, logout
User = get_user_model()
import cloudinary
from allauth.account.signals import user_signed_up


# Usually pre_delete is used to clean up, the folder after delete() is clicked


@receiver(pre_delete, sender=User)  # post_delete : you have to delete twice
# as the instance still exist after the save()
def delete_folder(sender, instance, *args, **kwargs):
    try:
        # Cloudinary
        # cloudinary.api.delete_resources_by_prefix(f"media_mediagallery/profile_images/{instance.pk}")
        # print('Deleted all image')
        # cloudinary.api.delete_folder(f"media_mediagallery/profile_images/{instance.pk}")  # Folder not empty
        # print(f'Deleted folder {instance.pk}')
        # default_storage.delete(instance.qr_image.name)
        path = os.path.join(os.getcwd(), f'media_mediagallery\profile_images\{instance.pk}')
        shutil.rmtree(path)
        print('Deleted all image and folder')

        # OS pc

    except Exception as e:
        print(e)


# @receiver(post_save, sender=User)  # post_delete : you have to delete twice
# # as the instance still exist after the save()
# def resize_pic(sender, instance, *args, **kwargs):
#     # user = User.objects.get(id=instance.id)
#     # cloudinary.api.delete_resources([user.profile_image])
#     try:
#         img = Image.open(instance.profile_image.name) # too fast
#         print(instance.profile_image.name)
#         if img.height > 300 or img.width > 300:
#             output_size = (300, 300)
#             img.thumbnail(output_size)
#             img.save(instance.profile_image.name)
#     except Exception as e:
#         print(e)


# pre_save.connect(delete_folder, sender=settings.AUTH_USER_MODEL)
# If you want to register the receiver function to several signals you may do it like this:
# @receiver([post_save, post_delete], sender=User)
# signal does not work when using it in a separate file

# When account is created via social, fire django-allauth signal to populate Django User record.
@receiver(user_signed_up)
@transaction.atomic
def populate_profile(request, sociallogin, user, **kwargs):
    """Signal, that gets extra data from sociallogin and put it to profile."""
    # User is created when EmailAddress is created but
    if sociallogin.account.provider == 'facebook':
        user_data = user.socialaccount_set.filter(provider='facebook')[0].extra_data
        email = user_data['email'].lower()
        first_name = user_data['first_name']
        last_name = user_data['last_name']

    if sociallogin.account.provider == 'google':
        user_data = user.socialaccount_set.filter(provider='google')[0].extra_data
        email = user_data['email']
        first_name = " ".join(user_data['name'].split(' ')[0:-1])
        last_name = user_data['name'].split(' ')[-1]

    user.email = email  # saves in both User, Social Account, User account
    user.is_customer = True
    user.save()

    # Email verification is auto with google but not for facebook
    # so we need to check our user is verifed or not
    if user.emailaddress_set.filter(verified=False).exists():
        account = EmailAddress.objects.get(email=user.email, verified=False)
        account.verified = True
        account.save()
    # now make a customer dor the corresponding user
    customer = Customer.objects.create(user=user)
    # student.attributes=self.cleaned_data.get(' attributes ')
    # Form must have this new attributes forms.charfield
    customer.first_name = first_name
    customer.last_name = last_name
    customer.save()
    return customer


'''
    sociallogin ==> Represents a social user that is in the process of being logged in
    To access any data you can use sociallogin as sociallogin <==> socialacount table same table
    sociallogin is an Instance before saving

    sociallogin.account is a SocialAccount instance
    sociallogin.is_existing  => True if the provider has a social account with us, False if it does not 
    sociallogin.user
    sociallogin.user.email
    
    sociallogin.email_addresses ==> Optional list of e-mail addresses retrieved from the provider.
    sociallogin.account.extra_data['picture']
    sociallogin.account.uid
    sociallogin.account.provider
    etc

'''

# @receiver(pre_social_login)
# def pre_social_login_populate_user(sender, request, sociallogin, **kwargs):
#     account = sociallogin.account
#     data = account.extra_data
#     user = account.user
#     if 'first_name' in data:
#         user.first_name = data['first_name']
#     if 'last_name' in data:
#         user.last_name = data['last_name']
#     user.save()





    # email_address = sociallogin.account.extra_data['email']
    # users = User.objects.get(email=email_address)
    # if users:
    #     perform_login(request, users, email_verification=None)
    #     raise ImmediateHttpResponse(redirect('main'))


# from django.contrib.auth.signals import user_logged_in
#
# @receiver(user_logged_in)
# def user_logged_in_(request, **kwargs):
#     storage = messages.get_messages(request)
#     storage.used = True
