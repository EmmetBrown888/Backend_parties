from django.http import JsonResponse
from rest_framework import status

uploaded_image_format = ['png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG']


def check_uploaded_image_format(photo):
    type_file = str(photo).split('.')[-1]
    if type_file not in uploaded_image_format:
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Ошибка загруженного файла. Загрузите фотографию формата .jpg, .jpeg, .png'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
