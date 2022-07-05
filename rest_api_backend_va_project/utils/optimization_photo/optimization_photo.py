import os
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from PIL import Image, UnidentifiedImageError

from user.models import User
from bid.models import Bid, BidImages


def optimization_photo(user: User, message_success: str, message_error: str, json_response: bool):
    """
    :param json_response: If True it will return JsonResponse(...)" else it will return the string "success" or "error"
    :param message_error: message to be returned on error
    :param message_success: message to be returned on success
    :param user: current user
    :return: JsonResponse(...)
    """
    try:
        path = 'images/' + str(user.photo)  # path uploaded photo

        photo_optimization = str(user.photo).split('.')
        photo_path = '/'.join(photo_optimization[0].split('/')[0:-1]) + '/' + f'{str(user.username)}'
        Image.open(f'images/{str(user.photo)}').convert('RGB').save(f'images/{photo_path}.webp', 'webp')
        user.photo = f'{photo_path}.webp'
        os.remove(path)
        user.save()
        if json_response:
            return JsonResponse(
                {
                    'status': 'success',
                    'message': message_success,
                    'data': {
                        'id': user.pk,
                        'username': user.username,
                        'first_name': user.first_name,
                        'sex': user.sex,
                        'birth_day': user.birth_day,
                        'city': user.city,
                        'email': user.email,
                        'photo': settings.BASE_URL + 'images/' + str(user.photo),
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            return 'success'
    except UnidentifiedImageError:
        if json_response:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': message_error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return 'error'


def converter_to_webp(bid: Bid, photos: BidImages, photo, key):
    path = 'images/' + str(photo)

    image_photo = Image.open(path)

    photo_optimization = str(photo).split('.')

    photo_path = '/'.join(photo_optimization[0].split('/')[0:-1]) + '/' + f'{str(bid.author.username)}' + f'-{str(bid.ad.title)}_{key}.webp'
    image_photo.save(f'images/{photo_path}', format="WebP", lossless = True)

    if key == 'photo_participants':
        photos.photo_participants = photo_path
    else:
        photos.photo_alcohol = photo_path
    
    os.remove(path)
    photos.save()