from rest_framework import serializers
from constructor import models


class ShortUrlRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ShortUrl

        fields = ['id', 'uuid', 'payload', ]


class ShortUrlPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ShortUrl
        fields = ['id', 'payload', ]
        extra_kwargs = {'uuid': {'required': False}}
        # optional_fields = ['uuid', ]

    def __init__(self, *args, **kwargs):
        super(ShortUrlPostSerializer, self).__init__(*args, **kwargs)
        print(args)
        print(kwargs, 'kjzhjghkfjgsajfgkjasgfkjgkjf')
