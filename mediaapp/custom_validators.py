from django.core.validators import ValidationError
import magic  # pip install python-magic-bin==0.4.14


# I could have used PIL since i am working wil only images

def file_size(image):
    if image.size > 1 * 1024 * 1024:
        raise ValidationError(f"{image.name} file is larger than 1mb.")
    return image


def file_type(image):
    valid_mime_types = ['image/jpeg', 'image/jpg']
    print('custom_validator')
    print(image)  # ONLY one file come in
    # recommend using at least the first 2048 bytes, as less can produce incorrect identification
    # if you read the whole file, it will consume time
    file_mime_type = magic.from_buffer(image.read(2048), mime=True)  # default read(-1), read the whole thing
    print("file_mime_type")
    print(file_mime_type)
    if file_mime_type.lower() not in valid_mime_types:
        raise ValidationError("Unsupported file")
    if str(image).split('.')[-1].lower() != "jpg":  # file to str
        print(str(image).split('.')[-1].lower()) # jpg
        print(type(str(image).split('.')[-1].lower()))
        print(str(image).split('.')[-1].lower() == "jpg")
        print(str(image).split('.')[-1].lower() != "jpg")
        raise ValidationError("Unacceptable file extension, must be either jpeg or jpg")
    return image
