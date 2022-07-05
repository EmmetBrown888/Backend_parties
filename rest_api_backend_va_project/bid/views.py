from loguru import logger
from django.http import JsonResponse
from django.db.models import Q, F
from rest_framework import generics, status, views
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import *
from .models import Bid, BidImages
from ad.models import Ad
from participant.models import Participant
from utils.permissions.permissions import AccountIsVerified
from utils.optimization_photo.optimization_photo import converter_to_webp


class BidRetrieveAPIView(APIView):
    """Get bid for pk"""
    serializer_class = BidSerializer
    permission_classes = [AccountIsVerified]

    @logger.catch
    def get(self, request, *args, **kwargs):
        ad_id = self.kwargs['ad_pk']
        bid_id = self.kwargs['bid_pk']

        ad = Bid.objects.filter(Q(ad__author__pk=request.user.pk) & Q(ad_id=ad_id)).values('pk')

        bid = Bid.objects \
            .filter(Q(ad__author__pk=request.user.pk) & Q(pk=bid_id)) \
            .values('id', 'photos', 'create_ad', 'author_id', 'author__username', 'author__photo')

        if not ad:
            return JsonResponse(
                {
                    'status': "error",
                    'message': "У вас нет данного объявления"
                },
                status=status.HTTP_204_NO_CONTENT
            )

        if not bid:
            return JsonResponse(
                {
                    'status': "error",
                    'message': "У вас нет данной заявки"
                },
                status=status.HTTP_204_NO_CONTENT
            )

        if ad and bid:
            return JsonResponse(
                {
                    'status': "success",
                    'message': "Ваша заявка успешно полученна",
                    'data': list(bid)
                },
                status=status.HTTP_200_OK
            )


class BidCreateView(views.APIView):
    """Create bid"""
    serializer_class = CreateBidSerializer
    permission_classes = [AccountIsVerified]

    @logger.catch
    def post(self, request, *args, **kwargs):
        data = self.request.data

        ad = Ad.objects.get(pk=data['id_ad'])
        participant = Participant.objects.filter(Q(user=self.request.user) & Q(ad_id=data['id_ad'])).values('pk')
        check_bid = Bid.objects.filter(Q(author_id=self.request.user.pk) & Q(ad_id=data['id_ad'])).values('pk')

        if check_bid or participant:
            return JsonResponse(
                {
                    'status': "error",
                    'message': "Вы уже подали заявку. Дождитесь ответа автора."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            photos = BidImages.objects.create(
                photo_participants=data['photo_participants'],
                photo_alcohol=data['photo_alcohol']
            )

            bid = check_bid.create(
                author=self.request.user,
                ad=ad,
                number_of_person=data['number_of_person'],
                number_of_girls=data['number_of_girls'],
                number_of_boys=data['number_of_boys'],
                photos=photos
            )

            for element in ['photo_participants', 'photo_alcohol']:
                if element == 'photo_participants':
                    converter_to_webp(bid, photos, photos.photo_participants, element)
                else:
                    converter_to_webp(bid, photos, photos.photo_alcohol, element)

            return JsonResponse(
                {
                    'status': "success",
                    'message': "Заявка успешно подана"
                },
                status=status.HTTP_201_CREATED
            )


class MyBidsRetrieveAPIView(APIView):
    """Get all my bids for ad"""
    serializer_class = MyBidsSerializer
    permission_classes = [AccountIsVerified]

    @logger.catch
    def get(self, request, *args, **kwargs):
        id_ad = self.kwargs['pk']
        bids = Bid.objects \
            .filter(Q(ad__author__pk=self.request.user.pk) & Q(ad_id=id_ad)) \
            .select_related('author', 'ad__author', 'ad') \
            .annotate(username=F('author__username'), photo_user=F('author__photo')) \
            .values(
            'id', 'username', 'photo_user', 'photos__photo_participants', 'photos__photo_alcohol',
            'author_id', 'number_of_person', 'number_of_girls', 'number_of_boys'
        )

        if bids:
            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'Ваши заявки успешно получены',
                    'data': list(bids)
                },
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse(
                {
                    'status': 'info',
                    'message': 'У вас пока нет заявок'
                },
                status=status.HTTP_204_NO_CONTENT
            )


class BidRejected(generics.DestroyAPIView):
    """Rejected bid"""
    serializer_class = BidSerializer
    permission_classes = [AccountIsVerified]

    @logger.catch
    def delete(self, request, *args, **kwargs):
        param = self.kwargs['pk']
        bid = Bid.objects.get(Q(pk=param) & Q(ad__author__pk=self.request.user.pk))

        if bid:
            """
                Уведомление user о том, что его заявку отклонили ( Websocket )
            """
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{str(bid.author.pk)}", {
                    "type": "user.gossip",
                    "event": "Reject Bid",
                    "message": f"Ваша заявка по объявлению {bid.ad.title} была отклоненна."
                }
            )

            bid.delete()
            bid.photos.delete()

            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'Данная заявка успешно отклонена'
                },
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Данной заявки не существует'
                },
                status=status.HTTP_204_NO_CONTENT
            )
