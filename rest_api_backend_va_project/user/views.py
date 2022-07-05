import os
from loguru import logger
from random import randint
from django.http import JsonResponse
from django.db import IntegrityError
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import generics, permissions, views, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.parsers import JSONParser

from .serializers import UserSerializers, \
    ChangePasswordSerializer, GetMeSerializer, UpdateUserSerializers, SubscriptionSerializer
from .models import *
from .tasks import send_letter_to_email
from utils.optimization_photo.optimization_photo import optimization_photo
from utils.format_images.format_images import check_uploaded_image_format
from utils.permissions.permissions import EmailIsVerified, AccountIsVerified


class UserListView(generics.ListAPIView):
    """Get all users (GET)"""
    serializer_class = UserSerializers
    permission_classes = [permissions.IsAdminUser]

    @logger.catch
    def get_queryset(self):
        return User.objects.all().only(
            'id', 'username', 'first_name', 'last_name', 'email', 'city',
            'birth_day', 'sex', 'photo', 'confirm_email', 'confirm_account'
        )


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Getting user by param (GET)"""
    serializer_class = UserSerializers
    permission_classes = [permissions.IsAdminUser]

    @logger.catch
    def get_queryset(self):
        return User.objects.all().only(
            'id', 'username', 'first_name', 'last_name', 'email', 'city',
            'birth_day', 'sex', 'photo', 'confirm_email', 'confirm_account'
        )


class UserUpdateData(generics.UpdateAPIView):
    """Change data about me"""
    serializer_class = UpdateUserSerializers
    permission_classes = [EmailIsVerified]
    parser_classes = (MultiPartParser, FormParser)
    queryset = User.objects.all()

    @logger.catch
    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            path = 'images/' + str(request.user.photo)

            if data['first_name']:
                request.user.first_name = data['first_name']

            if data['sex']:
                request.user.sex = data['sex']

            if data['birth_day']:
                request.user.birth_day = data['birth_day']

            if data['city']:
                request.user.city = data['city']

            if data['photo']:
                result = check_uploaded_image_format(data['photo'])
                if result:
                    return result
                request.user.photo = data['photo']
                os.remove(path)

            request.user.save()

            if data['photo']:
                result = optimization_photo(
                    request.user,
                    message_success='Ваши данные успешно измененны',
                    message_error='Ошибка загруженного файла. Загрузите фотографию формата .jpg, .jpeg, .png',
                    json_response=True
                )

                return result

            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'Ваши данные успешно измененны',
                    'data': {
                        'id': request.user.pk,
                        'username': request.user.username,
                        'first_name': request.user.first_name,
                        'sex': request.user.sex,
                        'birth_day': request.user.birth_day,
                        'city': request.user.city,
                        'email': request.user.email,
                        'photo': settings.BASE_URL + 'images/' + str(request.user.photo),
                    }
                },
                status=status.HTTP_200_OK
            )
        except KeyError:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'При отправке данных произошла ошибка. '
                               'Передайте следующие параметры: '
                               'Имя пользователя, Город, День рождения, Пол, Фото'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(views.APIView):
    """Auth - register"""
    parser_classes = (MultiPartParser, FormParser,)

    @logger.catch
    def post(self, request):
        try:
            data = request.data
            check_email_exist = User.objects.filter(email=data['email']).exists()
            if check_email_exist:
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Данный E-Mail уже используется. Введите другой E-Mail, либо войдите в аккаунт'
                    },
                    status=400
                )

            if data['password'] != data['confirm_password']:
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Пароли не совпадают!'
                    }, status=400
                )

            result = check_uploaded_image_format(data['photo'])
            if result:
                return result

            code = randint(123456, 987654)

            user = User.objects.create_user(
                data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                photo=data['photo'],
                city=data['city'],
                birth_day=data['birth_day'],
                sex=data['sex'],
                code_confirm=code
            )

            # Optimization upload photo
            optimization_photo(
                user,
                message_success='Ваши данные успешно измененны',
                message_error='Ошибка загруженного файла. Загрузите фотографию формата .jpg, .jpeg, .png',
                json_response=False
            )

            # Send letter to email
            email_body = 'Ваш код для подтверждения: ' + str(
                code) + '. Его следует использовать, чтобы подтвердить адрес электронной почты при регистрации.' + \
                        '\n\n' + f'Если вы {data["first_name"]} не запрашивали это сообщение, проигнорируйте его.' + \
                        '\n\n' + 'С уважением,' + '\n' + 'Команда VA'
            email_subject = 'Подтверждения вашего E-Mail'
            to_email = data['email']

            send_letter_to_email.delay(to_email, email_subject, email_body)

            return JsonResponse(
                {
                    'status': 'success'
                },
                status=201
            )
        except IntegrityError:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Введенное имя пользователя уже используется. Введите другое имя пользователя'
                },
                status=400
            )


class VerifyCode(views.APIView):
    """Confirm Email ===> entering the code that came to the mail"""

    @logger.catch
    def post(self, request):
        data = JSONParser().parse(request)
        user = User.objects.filter(code_confirm=int(data['code']))
        if user:
            user.update(confirm_email=True, code_confirm=None)
            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'E-Mail успешно подтвержден'
                },
                status=200
            )
        else:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Введенный код неправильный'
                },
                status=400
            )


class ForgetPassword(views.APIView):
    """Forget password"""

    @logger.catch
    def post(self, request):
        data = JSONParser().parse(request)
        user = User.objects.filter(email=data['email'])
        if user:
            code = randint(123456, 987654)
            user.update(code_confirm=code)

            # Send letter to email
            email_body = 'Ваш код: ' + str(
                code) + '. Его следует использовать, для восстановление доступа к вашему аккаунту.' + '\n\n' + \
                        f'Если Вы не запрашивали это сообщение, проигнорируйте его.' + '\n\n' + 'С уважением,' + \
                        '\n' + 'Команда VA'
            email_subject = 'Восстановление пароля'
            to_email = data['email']

            send_letter_to_email.delay(to_email, email_subject, email_body)

            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'На вашу почту отправленно письмо для восстановления аккаунта'
                },
                status=200
            )
        else:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'По вашему запросу ничего не найдено. Попробуйте ввести другой E-Mail.'
                },
                status=400
            )


class VerifyForgetPassword(views.APIView):
    """Forget password ===> entering the code that came to the mail"""

    @logger.catch
    def post(self, request):
        data = JSONParser().parse(request)
        user = User.objects.filter(code_confirm=int(data['code']))

        if user:
            user.update(code_confirm=None)
            return JsonResponse(
                {'status': 'success', 'message': 'Код успешно подтвержден'}, status=200
            )
        else:
            return JsonResponse(
                {'status': 'error', 'message': 'Введенный код неправильный'}, status=400
            )


class AddPasswordForgetPassword(views.APIView):
    """Forget password ===> enter new password"""

    @logger.catch
    def post(self, request):
        data = JSONParser().parse(request)
        user = User.objects.filter(email=data['email'])

        if user:
            if data['new_password'] == data['confirm_new_password']:
                user.update(password=data['new_password'])
                return JsonResponse(
                    {
                        'status': 'success',
                        'message': 'Пароль успешно изменен'
                    },
                    status=200
                )
            else:
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Введенные пароли не совпадают'
                    },
                    status=400
                )
        else:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Произошла ошибка. Попробуйте позже'
                },
                status=400
            )


class ChangePasswordView(generics.UpdateAPIView):
    """Auth - Change password ( into account )"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter().only('password')

    @logger.catch
    def put(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        user = User.objects.filter(pk=request.user.pk)

        if check_password(data['old_password'], request.user.password):
            if data['new_password'] == data['old_password']:
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Новый пароль не должен совпадает со старым паролем'
                    },
                    status=400
                )
            else:
                if data['new_password'] == data['confirm_new_password']:
                    user.update(password=make_password(data['new_password']))
                    return JsonResponse(
                        {
                            'status': 'success',
                            'message': 'Пароль успешно изменен'
                        },
                        status=200
                    )
                else:
                    return JsonResponse(
                        {
                            'status': 'error',
                            'message': 'Пароли не совпадают. Проверьте правильность введеных данных'
                        },
                        status=400
                    )
        else:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Вы ввели неправильный текущий пароль'
                },
                status=400
            )


class GetDataAboutMe(generics.ListAPIView):
    """Get data about me"""
    serializer_class = GetMeSerializer
    permission_classes = [EmailIsVerified]

    @logger.catch
    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk) \
            .only('id', 'username', 'first_name', 'last_name', 'email', 'city', 'birth_day', 'sex', 'photo',
                  'confirm_email', 'confirm_account')


class SubscriptionAPIView(generics.ListAPIView):
    """Get all subscriptions"""
    serializer_class = SubscriptionSerializer
    permission_classes = [AccountIsVerified]

    @logger.catch
    def get_queryset(self):
        return Subscription.objects.all()


class MySubscriber(views.APIView):
    """Get my subscription"""
    serializer_class = SubscriptionSerializer
    permission_classes = [AccountIsVerified]

    @logger.catch
    def get(self, request, *args, **kwargs):
        my_subscriber = Subscription.objects \
            .filter(author_id=request.user.pk) \
            .values('date_start', 'date_end')

        if my_subscriber:
            for sub in my_subscriber:
                date_start = sub['date_start']
                date_end = sub['date_end']
                days_left = str(date_end - date_start)

                days_left = [
                    {'time_left': {
                        'days': days_left[:2],
                        'hours': days_left[9:14]
                    }}
                ]

                return JsonResponse(
                    {
                        'status': 'success',
                        'data': list(my_subscriber) + days_left
                    },
                    status=status.HTTP_200_OK
                )
        else:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'У вас нет оплаченной подписки'
                },
                status=status.HTTP_404_NOT_FOUND
            )
