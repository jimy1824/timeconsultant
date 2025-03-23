from rest_framework import serializers
from constructor import models


class CurrencyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ['id', 'key', 'display_name', 'value_to_pkr', 'description']
