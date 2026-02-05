from rest_framework import serializers
from codex.models import Core, CoreBattleInfo, CoreUpgradeInfo, CoreEquippedMove, Garage
from codex.constants import RARITIES, CORE_TRACKS, RARITY_PRICES
from codex.serializers.move import MoveListSerializer


class CoreBattleInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreBattleInfo
        fields = '__all__'


class CoreUpgradeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreUpgradeInfo
        fields = '__all__'


class CoreEquippedMoveSerializer(serializers.ModelSerializer):
    move = MoveListSerializer(read_only=True)  # Nest move details

    class Meta:
        model = CoreEquippedMove
        fields = ['id', 'move', 'slot', 'created_at']


class CoreSerializer(serializers.ModelSerializer):
    battle_info = CoreBattleInfoSerializer(read_only=True)
    upgrade_info = CoreUpgradeInfoSerializer(read_only=True)
    equipped_moves = CoreEquippedMoveSerializer(many=True, read_only=True)

    class Meta:
        model = Core
        fields = '__all__'


class CoreGenerationRequestSerializer(serializers.Serializer):
    """Serializer for core generation API request"""
    name = serializers.CharField(max_length=120, required=True)
    rarity = serializers.ChoiceField(choices=RARITIES, required=True)
    track = serializers.ChoiceField(choices=CORE_TRACKS, required=True)
    garage_id = serializers.UUIDField(required=True)

    def validate_track(self, value):
        """Validate track is in allowed list."""
        if value not in CORE_TRACKS:
            raise serializers.ValidationError(
                f"Invalid track. Must be one of: {', '.join(CORE_TRACKS)}"
            )
        return value

    def validate_rarity(self, value):
        """Validate rarity is valid"""
        if value not in RARITIES:
            raise serializers.ValidationError(
                f"Invalid rarity. Must be one of: {', '.join(RARITIES)}"
            )
        return value

    def validate(self, data):
        """Custom validation for capacity and bits"""
        garage_id = data.get('garage_id')
        rarity = data.get('rarity')

        # Check garage exists and belongs to operator
        try:
            garage = Garage.objects.get(id=garage_id)
        except Garage.DoesNotExist:
            raise serializers.ValidationError({"garage_id": "Invalid garage ID"})

        # Check capacity
        if not garage.has_capacity():
            raise serializers.ValidationError({
                "garage": "Garage at capacity. Decommission cores to make room."
            })

        # Check operator has enough bits
        price = RARITY_PRICES[rarity]
        if garage.operator.bits < price:
            raise serializers.ValidationError({
                "bits": f"Insufficient credits. Need {price}, have {garage.operator.bits}"
            })

        # Store garage in validated data for use in view
        data['garage'] = garage
        data['price'] = price

        return data
