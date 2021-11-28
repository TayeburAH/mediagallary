import mimetypes

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import *
from .forms import *
from datetime import datetime
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, Http404
import imghdr
from PIL import Image


# Create your views here.
@login_required(login_url="/login_page")  # url
def galleries(request):
    categories = request.user.category_set.all()
    context = {
        'categories': categories,
        'active_link': 'Your Gallery'
    }
    return render(request, 'mediaapp/galleries.html', context=context)


@login_required(login_url="/login_page")  # url
def pictures(request, category_id):
    category = Category.objects.get(pk=category_id, user=request.user)
    pics = category.mediaimage_set.filter(trash__in=[False])  # works
    context = {
        'pics': pics,
    }

    return render(request, 'mediaapp/pictures.html', context=context)


@login_required(login_url="/login_page")  # url
def search(request):
    if request.GET.get("search_name"):
        pics = MediaImage.objects.filter(Q(image_name__icontains=request.GET.get("search_name")))
        context = {
            'pics': pics,
            'search': 'search'
        }
        return render(request, 'mediaapp/pictures.html', context=context)

    return redirect("galleries")


@login_required(login_url="/login_page")  # url
def create(request):
    form = CreateGallery()
    if request.method == "POST":
        form = CreateGallery(request.POST or None, request.FILES or None)
        print("create")
        print(form.is_valid())
        if form.is_valid():
            if form.cleaned_data['name']:
                category = form.save(commit=False)  # empty instance of model Category.create()
                category.user = request.user
                category.name = form.cleaned_data['name']
                category.description = form.cleaned_data['description']
                category.created = datetime.now()
                category.save()

            if form.cleaned_data['selected_category']:
                print(form.cleaned_data['selected_category'])
                print(type(form.cleaned_data['selected_category']))
                category = form.cleaned_data['selected_category']
                # As I used Model.... in the form, hence I will get the whole model
                # category = Category.objects.get(name=selected_category)

            # Now save photo
            images = form.files.getlist('image')  # Don't use form.cleaned_data['image']
            print(form.errors)
            print(images)  # THE FILES ARE IN InMemoryUploadedFile
            for image in images:
                obj = MediaImage.objects.create(user=request.user, image=image, category=category)
                obj.save()

            return redirect('create_gallery')
            # category, created = Category.objects.get_or_create(user=request.user, name=name, description=description)
            # Django Model() vs Model.objects.create()

    context = {
        'form': form,
        'active_link': 'Create Gallery'
    }
    return render(request, 'mediaapp/create_gallery.html', context=context)


def test(request):
    if request.method == 'GET' and request.GET.get('date', None):
        print(request.GET.get('time'))
        category = Category.objects.get(user=request.user)
        from datetime import datetime
        x = datetime.strptime(request.GET.get('datetime'), "%d/%m/%Y %I:%M %p")
        print(x)
        y = datetime.strptime(request.GET.get('date'), "%d/%m/%Y")
        print(y)
        z = datetime.strptime(request.GET.get('time'), "%I:%M %p").time()
        print(z)
        diff = request.GET.get('daterange').split('-')
        diff1 = diff[0].strip()
        diff2 = diff[1].strip()
        diff1 = datetime.strptime(diff1, "%m/%d/%Y")
        diff2 = datetime.strptime(diff2, "%m/%d/%Y")

        category.created = x
        category.save()
    return render(request, 'mediaapp/test.html')


@login_required(login_url="/login_page")  # url
def update_category(request, category_id):
    print(category_id)
    category = Category.objects.get(pk=category_id)
    print(request.GET.get('name'))
    print(request.GET.get('description'))
    if request.method == "GET":
        if request.GET.get('name'):
            # empty instance of model Category
            category.name = request.GET.get('name')
            category.save()
            print("saved")
            status = {
                "status": "ok",
                "name": category.name
            }
            return JsonResponse(status, safe=False)

        if request.GET.get('description'):
            category.description = request.GET.get('description')
            category.save()
            status = {
                "status": "ok",
                "description": category.description

            }
            return JsonResponse(status, safe=False)

        if request.GET.get('delete'):
            category.delete()
            status = {
                "status": "ok",
                "delete": "delete"
            }
            return JsonResponse(status, safe=False)
        return redirect('galleries')
        # category, created = Category.objects.get_or_create(user=request.user, name=name, description=description)
        # Django Model() vs Model.objects.create()


@login_required(login_url="/login_page")  # url
def update_image(request, pic_id):
    print(pic_id)
    media = MediaImage.objects.get(pk=pic_id)
    print(request.GET.get('name'))
    print(request.GET.get('description'))
    if request.method == "GET":
        if request.GET.get('name'):
            # empty instance of model Category
            media.image_name = request.GET.get('name')
            media.save()
            print("saved")
            status = {
                "status": "ok",
                "name": media.image_name,
                "type": imghdr.what(media.image)
            }
            from PIL import Image

            # read the image
            im = Image.open(media.image)

            # show image

            w, h = im.size  # Resolution
            print(f"{w}x{h}")
            print(str(len(im.fp.read())))  # image size
            return JsonResponse(status, safe=False)

        if request.GET.get('description'):
            media.description = request.GET.get('description')
            media.save()
            print("saved")
            status = {
                "status": "ok",
                "description": media.description
            }
            return JsonResponse(status, safe=False)

        if request.GET.get('delete'):
            media.trash = True
            media.save()
            status = {
                "status": "ok",
                "delete": "delete"
            }
            return JsonResponse(status, safe=False)

        return redirect(reverse('picture_gallery', kwargs={'category_id': media.category.id}))


@login_required(login_url="/login_page")  # url
def download(request, pic_id):
    # fill these variables with real values
    try:
        media = MediaImage.objects.get(pk=pic_id)
    except Exception as e:
        print(Exception)
        raise Http404

    # get the file path
    # fl_path = '/file/path'

    # Get the file name with ext
    im = Image.open(media.image.path)
    print("im")
    print(im)  # <PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=275x183 at 0x127D8D0FF70>
    ext = im.format
    # print(media.image_name) # name of the file, this is a attribute of Media Image class
    filename = media.image_name.replace(' ', '_')
    filename = filename + '.' + ext
    print(filename)

    # Guess the type of file
    mime_type, _ = mimetypes.guess_type(media.image.path)
    print("mime_type")
    print(mime_type)

    with open(media.image.path, "rb") as f:
        # if you put print(f) or print(f.read()) downloaded file format is destroyed
        # print(f) # contains an object
        # print(f.read()) # contains the bytes with b''
        # Set the HTTP header for sending to browser

        # response = HttpResponse(b'bytes', content_type=???)
        # Two ways => f.read() = b'bytes'  or  BytesIO().getvalue()=  b'bytes'

        response = HttpResponse(f.read(), content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response


@login_required(login_url="/login_page")  # url
def trash(request):
    pics = request.user.mediaimage_set.filter(trash__in=[True])
    context = {
        'pics': pics,
    }
    return render(request, 'mediaapp/trash.html', context=context)


@login_required(login_url="/login_page")  # url
def delete_permanent(request, pic_id):
    if request.GET.get('delete'):
        pic = request.user.mediaimage_set.filter(trash__in=[True], pk=pic_id)
        pic.delete()
        status = {
            "status": "ok",
            "delete": "delete"
        }
        return JsonResponse(status, safe=False)
    status = {
        "status": "Something wrong",
    }
    return JsonResponse(status, safe=False)
