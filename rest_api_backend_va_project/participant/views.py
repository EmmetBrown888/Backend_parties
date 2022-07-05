from loguru import logger
from django.http import JsonResponse
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import ParticipantSerializer
from .models import *
from ad.models import Ad
from bid.models import Bid
from user.models import User
from room_chat.models import Room
from utils.permissions.permissions import AccountIsVerified


class ParticipantRetrieveAPIView(generics.RetrieveAPIView):
    """Get participant for ad and bid"""
    serializer_class = ParticipantSerializer
    permission_classes = [AccountIsVerified]

    @logger.catch
    def get(self, request, *args, **kwargs):
        ad_id = self.kwargs['ad_pk']
        participant_id = self.kwargs['participant_pk']

        ad = Participant.objects \
            .filter(Q(ad__author__pk=request.user.pk) & Q(ad_id=ad_id)) \
            .values('pk')

        participant = Participant.objects \
            .filter(Q(ad__author__pk=request.user.pk) & Q(pk=participant_id)) \
            .values(
            'id', 'number_of_person', 'number_of_girls', 'number_of_boys', 'photos', 'create_ad', 'user_id',
            'user__username', 'user__photos__photo_participants', 'user__photos__photo_alcohol', 'user__sex'
        )

        if not ad:
            return JsonResponse(
                {
                    'status': "error",
                    'message': "У вас нет данного объявления"
                },
                status=status.HTTP_204_NO_CONTENT
            )

        if not participant:
            return JsonResponse(
                {
                    'status': "error",
                    'message': "У вас нет данного участника"
                },
                status=status.HTTP_204_NO_CONTENT
            )

        if ad and participant:
            return JsonResponse(
                {
                    'status': "success",
                    'message': "Ваша заявка успешно полученна",
                    'data': list(participant)
                },
                status=status.HTTP_200_OK
            )


def to_json(obj):
    photo_alcohol = '/images/' + str(obj.photos.photo_alcohol) if str(obj.photos.photo_alcohol) else ''
    photo_participants = '/images/' + str(obj.photos.photo_participants) if str(obj.photos.photo_participants) else ''
    return {
        "id_ad": obj.ad.pk,
        "participant_id": obj.pk,
        "user": {
            "id": obj.user.pk,
            "username": obj.user.username,
            "photo": '/images/' + str(obj.user.photo),
            'photo_participants': photo_participants,
            'photo_alcohol': photo_alcohol,
            "number_of_person": obj.number_of_person,
            "number_of_girls": obj.number_of_girls,
            "number_of_boys": obj.number_of_boys,
        }
    }


class MyParticipantsListAPIView(APIView):
    """Get all my participants"""
    serializer_class = ParticipantSerializer
    permission_classes = [AccountIsVerified]

    @logger.catch
    def get(self, request, *args, **kwargs):
        ad_id = self.kwargs['pk']

        participant = Participant.objects \
            .filter(Q(ad__author__pk=self.request.user.pk) & Q(ad_id=ad_id))

        participant_result = []
        for element in participant:
            result = to_json(element)
            participant_result.append(result)

        if participant.exists():
            return JsonResponse(
                {
                    'status': "success",
                    'message': "Ваша заявка успешно полученна",
                    'data': participant_result
                },
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse(
                {
                    'status': "error",
                    'message': "У вас нет участников"
                },
                status=status.HTTP_204_NO_CONTENT
            )


class ParticipantCreateView(generics.CreateAPIView):
    """Add participant"""
    serializer_class = ParticipantSerializer
    permission_classes = [AccountIsVerified]

    @logger.catch
    def post(self, request, *args, **kwargs):
        user_id = self.request.data['id_user']
        ad_id = self.request.data['id_ad']

        my_ad = Ad.objects.get(Q(author_id=self.request.user.pk) & Q(pk=ad_id))

        participant = Participant.objects.filter(user_id=user_id)

        if participant:
            return JsonResponse(
                {
                    'status': "error",
                    'message': "Данный пользователь уже находится в вашем списке участников"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if my_ad:
            user = User.objects.get(pk=user_id)
            check_user_bid = Bid.objects \
                .filter(author_id=user_id, ad__author__pk=self.request.user.pk)

            if check_user_bid:
                for bid in check_user_bid.values(
                        'number_of_person', 'number_of_girls', 'number_of_boys',
                        'photos__photo_participants', 'photos__photo_alcohol'
                ):
                    participant = Participant.objects \
                        .filter(Q(ad__author__pk=request.user.pk) & Q(ad_id=ad_id) & Q(user_id=user_id))
                    if participant:
                        return JsonResponse(
                            {
                                "status": "success",
                                "message": "У вас уже есть в участниках данный пользователь"
                            },
                            status=status.HTTP_404_NOT_FOUND
                        )
                    else:
                        photos = ParticipantImages.objects.create(
                            photo_participants=bid['photos__photo_participants'],
                            photo_alcohol=bid['photos__photo_alcohol']
                        )
                        participant = participant.create(
                            user=user,
                            ad=my_ad,
                            number_of_person=int(bid['number_of_person']),
                            number_of_girls=int(bid['number_of_girls']),
                            number_of_boys=int(bid['number_of_boys']),
                            photos=photos
                        )

                        #  Уведомление об успешном одобреннии заявки
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            f"user_{str(participant.user.pk)}", {
                                "type": "user.gossip",
                                "event": "Add in the participants",
                                "message": f"Ваша заявка по объявлению {participant.ad.title} была успешно одобренна.",
                                "id_ad": participant.ad.pk,
                                "participant_id": participant.pk,
                                "participant": {
                                    "user": {
                                        "id": participant.user.pk,
                                        "username": participant.user.username,
                                        "photo": '/images/' + str(participant.user.photo)
                                    },
                                    "information_about_bid": {
                                        "number_of_person": participant.number_of_person,
                                        "number_of_girls": participant.number_of_girls,
                                        "number_of_boys": participant.number_of_boys,
                                        "photos": {
                                            "photo_participants": '/images/' + str(
                                                participant.photos.photo_participants),
                                            "photo_alcohol": '/images/' + str(participant.photos.photo_alcohol),
                                        }
                                    }
                                }
                            }
                        )

                        ad = Ad.objects.get(pk=ad_id)
                        ad.participants.add(user)

                        room = Room.objects.get(ad_id=ad_id)
                        room.invited.add(user)

                check_user_bid.delete()

                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Вы успешно добавили пользователя в список участников"
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return JsonResponse(
                    {
                        'status': "error",
                        'message': "Данного user нет в ваших заявках"
                    },
                    status=status.HTTP_204_NO_CONTENT
                )
        else:
            return JsonResponse(
                {
                    'status': "error",
                    'message': "У вас нет созданного объявление"
                },
                status=status.HTTP_204_NO_CONTENT
            )


class ParticipantDestroyAPIView(generics.DestroyAPIView):
    """Reject participant"""
    serializer_class = ParticipantSerializer
    permission_classes = [AccountIsVerified]
    queryset = Participant.objects.all()

    @logger.catch
    def delete(self, request, *args, **kwargs):
        ad_id = kwargs['ad_pk']
        participant_id = kwargs['participant_pk']

        user = self.request.user.pk
        participant = Participant.objects.get(Q(ad__author__pk=user) & Q(ad_id=ad_id) & Q(pk=participant_id))

        my_ad = Ad.objects.get(author_id=user)

        if participant:
            user_pk = Participant.objects.get(pk=participant_id)
            user = User.objects.get(pk=user_pk.user.pk)
            my_ad.participants.remove(user)

            room = Room.objects.get(ad_id=ad_id)
            room.invited.remove(user)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{str(user.pk)}", {
                    "type": "user.gossip",
                    "event": "Kick Out from the party",
                    "message": f"Вас выгнали из вечеринки под названием {my_ad.title}."
                }
            )

            participant.delete()
            participant.photos.delete()

            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'Удаление прошло успешно'
                },
                status=status.HTTP_200_OK
            )

        else:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Данного участника нет у вас в списке'
                },
                status=status.HTTP_204_NO_CONTENT
            )
