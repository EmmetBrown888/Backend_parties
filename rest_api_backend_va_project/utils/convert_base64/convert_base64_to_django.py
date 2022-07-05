import base64
from django.core.files.base import ContentFile


def convert_base64_to_django_model(data):
    format, imgstr = data.split(';base64,')
    ext = format.split('/')[-1]
    data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    return data
