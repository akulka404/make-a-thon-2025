# log_items/serializers.py
from rest_framework import serializers
from log_items.models import FOOD_DATA

class USERD_Serializer(serializers.ModelSerializer):
    class Meta:
        model = FOOD_DATA
        fields = (
            'food_id',
            'food_name',
            'food_quality',
            # 'food_best_before',
            'stored_date',
            'stored_time',
            'expired_date',
            'expired_time',
            'food_usage',
            'image_url',
        )
        read_only_fields = ['stored_date', 'stored_time']
        # We mark stored_date and stored_time read-only so the client can’t overwrite them
