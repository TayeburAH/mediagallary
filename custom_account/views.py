from django.contrib.auth.views import PasswordContextMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import random
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from allauth.account.admin import EmailAddress
from django.contrib.auth.models import update_last_login
from datetime import datetime

User = get_user_model()


# Create your views here.
def main(request):
    return render(request, 'main.html')


def invalid(request):
    return HttpResponse('You are not allowed')


def send_otp(request):
    # OTP Code generate
    otp = str(random.randint(2000, 9000))
    # save otp in User model
    request.user.otp = otp
    request.user.save()
    print(otp)
    send_mail(
        # Subject
        'Helle from FoodMania',
        # Body
        f'Your OTP is {otp}. In order to activate your custom_account please type in the OTP',
        # From
        # os.environ['email'],
        settings.EMAIL_HOST_USER,
        # to
        [request.user.email],
        # What happens if it fails?
        fail_silently=True,

    )
    return redirect('otp_checker')


def otp_checker(request):
    if request.method == 'POST':
        if request.user.otp == request.POST.get('otp'):
            request.user.is_active = True
            request.user.save()
            # messages.success(request, 'Account activated')
            # logout(request)
            # return redirect('login_process')
            return redirect('main')
        else:
            messages.success(request, 'Wrong OTP')

    context = {
        'email': request.user.email,
    }
    return render(request, 'custom_account/otp.html', context)


def signup(request):
    if request.user.is_authenticated:  # always check whether logged in or not
        return redirect('home')
    else:
        form = CustomerForm()
        if request.method == 'POST':
            form = CustomerForm(request.POST or None)  # Pass in the data for validation
            if form.is_valid():  # to check and show form.errors in templates
                form.save()
                messages.success(request,
                                 'Account created')  # we dont have to pass it in, message is sent to all templates
                user = authenticate(request, email=request.POST.get('email'),
                                    password=request.POST.get('password2'))
                login(request, user)
                return redirect('send_otp')

        context = {'form': form}
        return render(request, 'custom_account/signup.html', context)


def login_process(request):
    # Used HTML Raw Form
    if request.method == 'GET':  #
        request.session['from'] = request.META.get('HTTP_REFERER', '/')
    if request.user.is_authenticated:
        return redirect('main')
    else:
        if request.method == 'POST':
            user = authenticate(request, email=request.POST.get('email').lower(),
                                password=request.POST.get('password'))
            if user is not None:
                login(request, user)
                # update_last_login(None, user)
                user.customer.last_login = datetime.now()
                if user.is_active:
                    return redirect('main')
                else:
                    return redirect('send_otp')
            else:
                if EmailAddress.objects.filter(email=request.POST.get('email')).exists():
                    social_user = EmailAddress.objects.get(email=request.POST.get('email'))
                    user = User.objects.get(email=request.POST.get('email'))
                    messages.error(request, f'The account {social_user.user} was created through '
                                            f'{user.socialaccount_set.all()[0].provider.capitalize()}. '
                                            f'Please click on the {user.socialaccount_set.all()[0].provider.capitalize()} button above to enter your account.')
                else:
                    messages.error(request, 'User or password incorrect.')

    context = {}  # no need to pass any form
    return render(request, 'custom_account/login.html', context)


def logout_process(request):
    logout(request)
    # messages.success(request, 'User logged out.')
    context = {}
    return redirect('login_process')


def edit_profile(request):
    if request.method == 'GET':
        request.session['from'] = request.META.get('HTTP_REFERER', '/')
    customer = get_object_or_404(Customer, user=request.user)
    form = CustomerUpdateForm(instance=customer or None)
    form.fields['DOB'].widget.attrs.update({'value': customer.user.DOB.strftime("%Y/%m/%d")})

    if request.method == 'POST':
        form = CustomerUpdateForm(request.POST or None, instance=customer)
        if form.is_valid():  # to check and show form.errors in templates
            customer = form.save(commit=False)
            customer.user.DOB = form.cleaned_data['DOB']  # must use user.save()
            print(form.cleaned_data['DOB'])
            # customer.user = request.user  # this is missing from form, so i have to save it
            # # here as I need request.user which i cant get in super(Customer,self).save(commit=False)
            #
            # # since I redesigned the address field, I need to personally
            # # save it
            customer.save()
            customer.user.save()
            messages.success(request,
                             'Account Updated.')  # we don't have to pass it in, message is sent to all templates
            return redirect(request.session['from'])

    context = {'form': form}
    return render(request, 'custom_account/edit_profile.html', context)


def delete_process(request):
    if request.method == 'POST':
        user = authenticate(request, email=request.user.email, password=request.POST.get('password'))
        if user is not None:
            user.delete()
            return redirect('main')
        else:
            messages.error(request, 'password incorrect')

    context = {}  # no need to pass any form
    return render(request, 'custom_account/delete_process.html', context)


def password_reset_request(request):
    password_reset_form = PasswordResetForm()
    if request.method == "POST":
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            print(data)
            user = User.objects.get(email=data.lower())
            subject = 'Request for password change'
            password_reset_email = "registration/password_reset_email.html"
            context = {
                "email": user.email,
                'domain': domain,
                # 'site_name': site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'https',
            }

            email = render_to_string(password_reset_email, context)
            try:
                send_mail(subject, email, os.environ['email'], [data], fail_silently=False)
                # (subject, message, from_email, recipient_list[])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect("password_reset_done")

    context = {"form": password_reset_form}
    return render(request, "registration/password_reset.html", context)
