from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db.models.signals import pre_delete
from django.core.files.storage import default_storage as storage
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from setuptools.sandbox import save_path
from io import BytesIO
from .custom_validators import *
import os
import shutil
from PIL import Image
import shutil
import time
import cloudinary
from cloudinary import uploader
from django.conf import settings
import re

User = settings.AUTH_USER_MODEL


# Create your models here.

# <------------------  Manager ------------------------->
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        You need to use validation
        """
        user = self.model(
            email=email,
        )

        user.set_password(password)  # or put it in   user = self.model( password = password)
        user.is_staff = False
        user.is_superuser = False
        user.is_customer = False
        user.is_seller = False
        user.is_active = True
        # last save it
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        No need to validate
        """

        user = self.create_user(
            email=email,
            password=password,

        )
        user.is_staff = True
        user.is_superuser = True
        user.is_customer = True
        user.is_seller = True

        # last save it
        user.save(using=self._db)
        return user


# <------------------   User ------------------------->

@transaction.atomic
def profile_image_file_path(instance, filename):
    # OS
    # delete same name files to avoid random letters adding to file name
    # print(filename)  # gives the file name with extension

    try:
        shutil.rmtree(os.path.join(os.getcwd(), f'media_mediagallery\profile_images\{instance.pk}'))
        # cloudinary.api.delete_resources_by_prefix(f"media_mediagallery/profile_images/{instance.pk}")
        print('Deleted all image')
        # cloudinary.api.delete_folder(f"media_mediagallery/profile_images/{instance.pk}")  # Folder not empty
        print('Deleted folder')
        # Cloudinary
    except Exception as e:
        print(e)

    return f'profile_images/{instance.pk}/{filename}'

    # Cloudinary
    # try:
    #     cloudinary.api.delete_resources_by_prefix(f"media_mediagallery/profile_images/{instance.pk}")
    # except Exception as e:
    #     print(e)
    # return f'profile_images/{instance.pk}/{filename}'


# Default profile image
def default_image_file_path():
    return 'default_profile_image/default.png'


# validators=[validate_your_email,
class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(verbose_name='Email', max_length=50, unique=True,
                             null=True, blank=True, validators=(validate_your_email, ))
    date_joined = models.DateField(verbose_name='date joined',
                                   auto_now_add=True)  # when custom_account gets created the date gets set
    last_joined = models.DateField(verbose_name='last joined',
                                   auto_now=True)  # updates the value of field to current time and date every time the Model.save() is called

    otp = models.CharField(max_length=4, null=True, blank=True)
    profile_image = models.ImageField(upload_to=profile_image_file_path, default=default_image_file_path, null=True,
                                      blank=True)
    first_name = models.CharField(max_length=60, null=True, blank=True)
    last_name = models.CharField(max_length=60, null=True, blank=True)
    DOB = models.DateField(null=True, blank=True, verbose_name='Date of birth')
    # Must include
    is_active = models.BooleanField(default=True)  # only this true
    is_staff = models.BooleanField(default=False)  # a admin user; non super-user
    is_superuser = models.BooleanField(default=False)  # a superuser

    # add more multi_user
    is_customer = models.BooleanField(default=False)  # a customer
    # notice the absence of a "Password field", id, last_login that is built in.

    objects = UserManager()  # To link it with UserManager(BaseUserManager)

    USERNAME_FIELD = 'email'

    # REQUIRED_FIELDS = ['username']  # Besides email what must be required

    def __str__(self):
        return self.email  # Django uses this when it needs to convert the object into string

    @property
    def profile_imgURL(self):  # you can also use {{ user.profile_image.url }}
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url

    @transaction.atomic
    def save(self, *args, **kargs):
        #  name remains same before save()
        super(User, self).save(*args, **kargs)
        #  name changes after save() into _ _ in empty spaces etc
        # Cloudinary
        # public_id = self.profile_image.name.split('/')[-1]
        # image_read = storage.open(self.profile_image.name, 'rb')
        # image = Image.open(image_read)
        # # Delete the old picture
        # cloudinary.api.delete_resources([self.profile_image.name, ])
        # if image.height > 200 or image.width > 200:
        #     size = 200, 200
        #     # Create a buffer to hold the bytes in your computer memory
        #     imageBytes = BytesIO()
        #     # Resize
        #     image.thumbnail(size, Image.ANTIALIAS)
        #     # Save the image as jpeg to the buffer
        #     image.save(imageBytes, image.format)
        #
        #     cloudinary.uploader.upload(imageBytes.getvalue(),
        #                                folder=f"media_mediagallery/profile_images/{self.pk}",
        #                                public_id=f"{public_id}")

        # # For PC os
        img = Image.open(self.profile_image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.profile_image.path)

    def image_tag(self):  # use image_tag in list_display
        if self.profile_image:
            return mark_safe('<img src="/media_mediagallery/%s" width="50" height="50" />' % self.profile_image)
        else:
            return mark_safe('<img src="/media_mediagallery/default.jpg" width="50" height="50" />')

    image_tag.short_description = 'Profile image'  # name of the column will be now Pictures

    # add more function here

    # Must be included
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


    # Works fine
    #  # deletes the old picture when updating it
    # def save(self, *args, **kwargs):
    #     try:
    #         this = User.objects.get(id=self.pk)  # getting the old picture
    #         if this.profile_image != self.profile_image:
    #             this.profile_image.delete()
    #     except:
    #         pass
    #     super(User, self).save(*args, **kwargs)  # carry on with normal save method

    # # Works fine
    # def delete(self, *args, **kwargs):
    #     try:  # Delete the data before
    #         self.profile_image.delete()  # django clan up isnit fast enough
    #         os.rmdir(os.path.join(os.getcwd(), f'media_mediagallery\profile_images\{self.pk}'))
    #     except FileNotFoundError:
    #         pass
    #     super(User, self).delete(*args, **kwargs)  # carry on with normal delete method


# @receiver(pre_delete, sender=User)  # post_delete : you have to delete twice
# # as the instance still exist after the save()
# def delete_folder(sender, instance, *args, **kwargs):
#     try:  # instance.profile_image.delete()  will delete your default.png
#         path = os.path.join(os.getcwd(), f'media_mediagallery\profile_images\{instance.pk}')
#         shutil.rmtree(path)
#
#     except OSError:
#         pass


# # Customer information
# class Division(models.Model):
#     name = models.CharField(max_length=40)
#
#     def __str__(self):
#         return self.name
#
#
# class City(models.Model):
#     division = models.ForeignKey(Division, on_delete=models.CASCADE)
#     name = models.CharField(max_length=40)
#
#     class Meta:
#         verbose_name_plural = 'Cities'
#
#     def __str__(self):
#         return self.name
#
#
# class Zip(models.Model):
#     city = models.ForeignKey(City, on_delete=models.CASCADE)  # city_id
#     name = models.CharField(max_length=40)
#
#     class Meta:
#         verbose_name_plural = 'Zip Codes'
#
#     def __str__(self):
#         return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateField(verbose_name=' last login', auto_now=True)

    # division = models.ForeignKey(Division, on_delete=models.SET_NULL, blank=True, null=True)
    # city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
    # zip = models.ForeignKey(Zip, on_delete=models.SET_NULL, blank=True, null=True)
    # address = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.first_name


'''
AUTH_USER_MODEL = 'custom_account.User'    #<app_name>.custom_model_name
change from built-in user model to ours
'''

'''
'django_cleanup',
pip install django-cleanup

Instruction to delete files in Django
pip install django - cleanup
INSTALLED_APPS = (
    ...
    'django_cleanup',  # should go after your apps

'''

'''
Now you can't use  from django.contrib.auth.models import User
but you have to use 

from django.conf import settings
User = settings.AUTH_USER_MODEL
'''

'''
In other models, 
Example user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

So Copy this now
from django.conf import settings
User = settings.AUTH_USER_MODEL

or use

from django.contrib.auth import get_user_model
User = get_user_model()
'''

'''
to point it out to static directory, create it

settings.py
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # look for static directory
]
'''

'''
MEDIA_URL = '/media_mediagallery/'                       # to make a url
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_mediagallery')
 This is where we are going to upload the pictures into the database, and stores it in media_cdn

 STATIC_ROOT is missing as its only needed when you upload in server
if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, '')
 to upload the pictures into the database, but keep it 'static/images'

BASE_DIR = 'http://127.0.0.1:8000'

'''

'''
For media_mediagallery files
In root urls.py 

from django.conf.urls.static import static
from django.conf import settings

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    pip install Pillow

'''
