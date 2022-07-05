from loguru import logger
from django.http import JsonResponse
from django.db.models import Q
from rest_framework import status, generics, views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .serializers import *
from .models import *
from utils.mixins.pagination import PaginationHandlerMixin
from utils.permissions.permissions import AccountIsVerified


class BasicPagination(PageNumberPagination):
    page_size_query_param = 'count'


class MyRooms(APIView):
    """Get all my rooms where i participant"""
    permission_classes = [AccountIsVerified]

    @logger.catch
    def get(self, request):
        rooms = Room.objects.all().filter(invited__pk=request.user.pk)
        if rooms:
            serializer = RoomSerializers(rooms, many=True)
            return Response(
                {
                    "status": "success",
                    "data": serializer.data
                }
            )
        else:
            return JsonResponse(
                {
                    'status': "error",
                    'message': "У вас пока нет комнат"
                },
                status=status.HTTP_204_NO_CONTENT
            )


class VoteCreate(views.APIView):
    permission_classes = [AccountIsVerified]

    def post(self, request):
        ad_id = request.data['id_ad']  # id объявления
        candidate = request.data['id_candidate']  # User против которого создают голосование
        check_user = Room.objects.filter(invited__pk=request.user.pk).exists()
        if not check_user:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Вас нет в данной комнате'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if int(candidate) == request.user.pk:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Вы не можете начать голосование против себя'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        check_author = Room.objects.filter(ad__author__pk=candidate).exists()

        if check_author:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Вы не можете начать голосование против автора'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        room = Room.objects.get(
            Q(ad__id=ad_id) &
            ~Q(ad__author__pk=candidate) &
            Q(invited__pk=int(candidate))
        )

        if room:
            candidate = User.objects.get(pk=candidate)
            vote = Vote.objects.create(
                author=request.user,
                candidate=candidate
            )

            vote.voted.add(request.user)

            room.voting.add(vote)

            return JsonResponse(
                {
                    'status': 'success',
                    'message': ' Вы успешно начали голосование'
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Данного кандидата нет в комнате'
                },
                status=status.HTTP_204_NO_CONTENT
            )


class Voting(APIView):
    permission_classes = [AccountIsVerified]

    def post(self, request):
        vote_type = request.data['vote_type']  # kick_out / ban_writting (Celery)
        action = request.data['action']
        ad_id = request.data['id_ad']
        vote_id = request.data['vote_id']
        room = Room.objects.filter(
            Q(ad__id=ad_id) & Q(invited__pk=request.user.pk) & ~Q(blocked_user__pk=request.user.pk)).exists()

        if not room:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Вас нет в данной комнате'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        check_user = Vote.objects.filter(voted__pk=request.user.pk).exists()
        if check_user:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Вы уже проголосовали'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        vote = Vote.objects.get(pk=vote_id)
        vote.to_vote(request.user, action)

        count = vote.voting_count()

        return JsonResponse(
            {
                'status': 'success',
                'data': {
                    "count": count
                }
            },
            status=status.HTTP_200_OK
        )


class Messages(APIView, PaginationHandlerMixin):
    """Get all messages for room"""
    permission_classes = [AccountIsVerified]
    pagination_class = BasicPagination

    @logger.catch
    def get(self, request, pk):
        messages = Chat.objects.all().filter(Q(room_id=pk) & Q(room__invited__pk=request.user.pk))
        if messages:
            page = self.paginate_queryset(messages)
            if page is not None:
                serializer = self.get_paginated_response(ChatSerializer(page, many=True).data)
            else:
                serializer = ChatSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {
                    'status': "error",
                    'message': "У вас пока нет сообщений"
                },
                status=status.HTTP_204_NO_CONTENT
            )


class MessageRejected(generics.DestroyAPIView):
    """Rejected message"""
    permission_classes = [AccountIsVerified]

    def delete(self, request, *args, **kwargs):
        room_id = self.kwargs['room_id']
        id_message = self.kwargs['id_message']

        message = Chat.objects.get(Q(room_id=room_id) & Q(pk=id_message))

        if (request.user.pk != message.user.pk) and (request.user.pk != message.room.ad.author.pk):
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Вы не можете удалить сообщение которое не принадлежит вам'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        message.delete()
        if message.images:
            message.images.delete()

        return JsonResponse(
            {
                'status': "success",
                'message': 'Удаление прошло успешно'
            },
            status=status.HTTP_200_OK
        )
