from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db import transaction
from django.db.models import Q
# from .models import Division, City, Zip
from .models import Customer
# call this UserAdminCreationForm, UserAdminChangeForm in your views.py
from datetime import datetime
from django.conf import settings

User = get_user_model()


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'password1',
        'placeholder': 'Enter password here'
    }))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        'class': 'password2',
        'placeholder': 'Enter same password here'
    }))
    email = forms.CharField(label='Email or mobile number', widget=forms.EmailInput(attrs={
        'class': 'email',
        'placeholder': 'email'
    }))

    class Meta:
        model = User
        fields = []  # add the required field here

    def clean(self):
        '''
        Verify both passwords match.
        '''
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 is not None and password1 != password2:
            self.add_error("password2", "Your passwords must match")
        return cleaned_data

    # All emails are saved as lower case, lower case the email you get in the form and check
    # Otherwise it will be saved as new email same, but upper and lowercase mixtures
    # def clean_email(self):
    #     email = self.cleaned_data['email'].lower()
    #     try:
    #         user = User.objects.get(email=email)
    #     except Exception as e:
    #         return email
    # raise forms.ValidationError("Email already exists")
    #     self.add_error("email", "Email already exists")
    @transaction.atomic
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password2"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'password', 'is_active', 'is_superuser']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


# <---------------------------------------------CustomerForm----------------------------------------------->
# Extending UserAdminCreationForm
# Making extra form fields
# filling Customer model fields at the same time from extra form fields

class CustomerForm(UserAdminCreationForm):
    # Make new fields, so I have to personally save it, must be here

    first_name = forms.CharField(required=False, label='First name', widget=forms.TextInput(attrs={
        'class': 'first_name',
        'id': 'first_name-id',
        'placeholder': 'Enter your code here'

    }))

    # Redesigned last_name, so I have to personally save it, must be here
    last_name = forms.CharField(required=False, label='Last name', widget=forms.TextInput(attrs={
        'class': 'zip_code',
        'id': 'zip-id',
        'placeholder': 'Enter last name here'

    }))
    DOB = forms.CharField(label='Date of birth', widget=forms.TextInput(attrs={
        "autocomplete": "off",
    }))

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']  # default DOB from User will not work

        # name = models.CharField(null=False, blank=False)
        # user = models.OneToOneField(User, on_delete=models.CASCADE)
        # date_created = models.DateField(verbose_name='date joined',auto_now_add=True)
        # last_login = models.DateField(verbose_name=' last login', auto_now=True)

    def clean_DOB(self):
        DOB = self.cleaned_data.get("DOB")
        print(DOB)
        print(type(DOB))
        DOB = datetime.strptime(DOB, "%Y/%m/%d")
        return DOB

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)  # stop save() # Model name of model but instance created
        # user.attributes=self.cleaned_data.get(' attributes ')
        user.is_customer = True
        user.is_active = False
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        print(self.cleaned_data.get('DOB'))
        print(type(self.cleaned_data.get('DOB')))
        user.DOB = self.cleaned_data.get('DOB')
        user.save()
        customer = Customer.objects.create(user=user)
        # student.attributes=self.cleaned_data.get(' attributes ')
        # Form must have this new attributes forms.charfield
        customer.first_name = self.cleaned_data.get('first_name')
        customer.last_name = self.cleaned_data.get('last_name')
        customer.save()
        return customer


# <---------------------------------------------CustomerUpdateForm ----------------------------------------------->

class CustomerUpdateForm(forms.ModelForm):
    # Redesigned address, but I have to personally save it, must be above fields=[]
    DOB = forms.CharField(label='Date of birth', widget=forms.TextInput(attrs={
                              "autocomplete": "off",
                          }))

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name']



        # fields = ['first_name', 'last_name', 'division', 'city', 'zip', 'address']

        # def __init__(self, *args, **kwargs):
        #     super(CustomerUpdateForm, self).__init__(*args, **kwargs)
        #     self.fields['first_name'].initial = self.instance.first_name  # Initialize with instance
        #     self.fields['last_name'].initial = self.instance.last_name  # Initialize with instance
        '''
        override the __init__ method is to define or exclude fields dynamically, based on some condition.
        del(self.fields['non_editable_field'])
        .queryset
        .required = True|False
        .initial = your value
        '''
    #     if self.instance.pk and self.instance.address:
    #         self.fields['address'].queryset = self.instance.address
    #
    #     if 'division' in self.data:
    #         try:
    #             division_id = int(self.data.get('division'))
    #             self.fields['city'].queryset = City.objects.filter(division_id=division_id).order_by('name')
    #         except (ValueError, TypeError):
    #             pass  # invalid input from the client; ignore and fallback to empty City queryset
    #     # For updating purpose
    #     elif self.instance.pk and self.instance.city:
    #         self.fields['city'].queryset = self.instance.division.city_set.all().order_by('name')
    #
    #     if 'city' in self.data:
    #         try:
    #             city_id = int(self.data.get('city'))
    #             self.fields['zip'].queryset = Zip.objects.filter(city_id=city_id).order_by('name')
    #         except (ValueError, TypeError):
    #             pass  # invalid input from the client; ignore and fallback to empty City queryset
    #     # For updating purpose
    #     elif self.instance.pk and self.instance.zip:
    #         self.fields['zip'].queryset = self.instance.city.zip_set.all().order_by('name')
    #

    def clean_DOB(self):
        DOB = self.cleaned_data.get("DOB")
        print(DOB)
        print(type(DOB))
        DOB = datetime.strptime(DOB, "%Y/%m/%d")
        return DOB

# <---------------------------------------------Password Reset ----------------------------------------------->


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

    def clean_email(self):
        data = self.cleaned_data['email'].lower()

        try:
            user = User.objects.get(Q(email=data) & Q(is_active=True))
        except Exception as e:
            raise forms.ValidationError("Email does not exist in database")
        return data
        # self.add_error("email", "Email already exists")


# <---------------------------Password Change form for mobile users -------------------------------------->

class PasswordChange(forms.Form):
    """
    A form for changing password. Includes all the required
    fields, plus a repeated password.
    """
    new_password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'password1',
        'placeholder': 'Enter password here'
    }))
    new_password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        'class': 'password2',
        'placeholder': 'Enter same password here'
    }))

    def clean(self):
        '''
        Verify both passwords match.
        '''
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        if password1 is None and password1 != password2:
            self.add_error("new_password2", "Your passwords must match")
        return cleaned_data
