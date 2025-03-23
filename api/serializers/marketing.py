from rest_framework import serializers
from constructor import models


class MarketingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MarketingCard

        fields = ['id', 'card_type', 'heading', 'priority',
                  'grid_card_img_front', 'grid_card_img_back',
                  'list_card_img_front', 'list_card_img_back', 'detail_page_img', ]


class MarketingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MarketingCard
        fields = ['id', 'card_type', 'detail_page_img', 'heading', 'content']
