from rest_framework import serializers

from .models import Bid
from user.serializers import UserSerializers
from ad.serializers import AdSerializer


class BidSerializer(serializers.ModelSerializer):
    author = UserSerializers(read_only=True)
    ad = AdSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = ('id', 'author', 'ad', 'number_of_person', 'number_of_girls', 'number_of_boys', 'photos', 'create_ad')


class CreateBidSerializer(serializers.ModelSerializer):
    author = UserSerializers(read_only=True)

    class Meta:
        model = Bid
        fields = ('id', 'author', 'number_of_person', 'number_of_girls', 'number_of_boys', 'photos', 'create_ad')


class MyBidsSerializer(serializers.ModelSerializer):
    author = UserSerializers(read_only=True)

    class Meta:
        model = Bid
        fields = ('id', 'author', 'number_of_person', 'number_of_girls', 'number_of_boys')
