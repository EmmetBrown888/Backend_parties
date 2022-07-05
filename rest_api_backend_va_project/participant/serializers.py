from rest_framework import serializers

from .models import Participant, ParticipantImages
from user.serializers import UserSerializers
from ad.serializers import AdSerializer


class ParticipantPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantImages
        fields = ('photo_participants', 'photo_alcohol')


class ParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializers(read_only=True)
    ad = AdSerializer(read_only=True)
    photos = ParticipantPhotosSerializer()

    class Meta:
        model = Participant
        fields = ('id', 'user', 'ad', 'number_of_person', 'number_of_girls', 'number_of_boys', 'create_ad', 'photos')
