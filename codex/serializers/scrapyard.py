from rest_framework import serializers
from codex.models import Scrapyard


class ScrapyardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrapyard
        fields = [
            'id',
            'items_for_sale',
            'bundles',
            'weekly_deal',
            'purchase_logs',
            'decommed_cores',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
