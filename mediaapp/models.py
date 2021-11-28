from django.db import models
from django.contrib.auth import get_user_model
from .custom_validators import file_size, file_type

User = get_user_model()


# Create your models here.

class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Enter Category')
    description = models.TextField(blank=True)
    # Must put blank=True, to stop showing The field is required, Than customize in the clean(self):
    # to make it required for in relation with some fields
    created_date = models.DateTimeField(null=True, auto_now_add=True)
    last_updated = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return self.name

    def show_created(self):
        return self.created_date


def upload_to_folder(instance, filename):
    return f'media_files/{instance.user.pk}/{filename}'


class MediaImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=upload_to_folder, null=False, blank=False, validators=(file_size,file_type))
    # this validator will work if it is used with its ModelForm
    created_date = models.DateTimeField(null=True, auto_now_add=True)
    # image.url to access its url
    image_name = models.CharField(max_length=50, null=True, blank=True)
    last_updated = models.DateTimeField(null=True, auto_now=True)
    trash = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)

    # def label_image(self):
    #     self.image_name = str()


# on_delete = models.CASCADE
# on_delete=models.SET_NULL, null = True

# image = models.ImageField()
# image.url to access its url than use it in src in html


# pimage = models.URLField()
# use it as pimage in src html
'''

1. SomeModel.objects.create(firstname='ricky', lastname='ticky')


2. 
    obj = Person(first_name='John', last_name='Lennon', birthday=date(1940, 10, 9))
    obj.save()


3. 
obj, created = Person.objects.get_or_create(
    first_name='John',
    last_name='Lennon',
    defaults={'birthday': date(1940, 10, 9)},
)
'''
