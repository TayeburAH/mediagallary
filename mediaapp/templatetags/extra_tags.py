from django import template
from mediaapp.models import MediaImage
from PIL import Image
from io import BytesIO

register = template.Library()


@register.filter(name='default_image_name')  # invalid filter
def default_image_name(image_name):
    print(image_name)
    image_name = image_name.split('\\')[-1]
    return image_name
    # {{      }}


@register.simple_tag  # filter working
def default_image_name(image_name):
    print("image")
    print(image_name)
    image_name = image_name.split('\\')[-1]
    return image_name
    # simple_tag
    # {%      %}
    # Used to perform only function as it can take many arguments
    # Cannot be used with if
    # {%  default_image_name pic.image.path %}


@register.filter(name='check_image')
def check_image(media):
    media = MediaImage.objects.get(pk=media.pk)
    if media.image_name:
        return True
    return False
    # Filter
    # {%      %}, {{     }}
    # This is used with if
    # variable|function format
    # {% if pic|check_image %}
    # <p>{{  pic|check_image }}</p>   both works


@register.filter(name='image_type')
def image_type(media):
    name = MediaImage.objects.get(pk=media.pk).image_name
    print(name)
    media = MediaImage.objects.get(pk=media.pk)
    im = Image.open(media.image.path)
    print(im.format)
    return name + "." + im.format


@register.simple_tag  # filter working
def image_format(media):
    media = MediaImage.objects.get(pk=media.pk)
    im = Image.open(media.image.path)
    return im.format


@register.simple_tag
def image_resolution(media):
    media = MediaImage.objects.get(pk=media.pk)
    im = Image.open(media.image.path)
    w, h = im.size
    return f"{w}x{h}"


@register.simple_tag
def image_bytes(media):
    media = MediaImage.objects.get(pk=media.pk)
    im = Image.open(media.image.path)
    in_memory = BytesIO()
    im.save(in_memory, im.format)
    return f"{round(in_memory.tell() / 1024, 1)} KB"


@register.filter(name='check_description')  # works, but {% if pic.description %} also works
def check_description(media):
    description = MediaImage.objects.get(pk=media.pk).description
    if description:
        return True
    return False
