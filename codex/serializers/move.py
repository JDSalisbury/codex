"""
Move Serializers
Handles API serialization for Move model and related operations.
"""
from rest_framework import serializers
from codex.models import Move
from codex.constants import MOVE_FUNCTIONS, MOVE_DMG_TYPES, CORE_TYPES, RARITIES


class MoveSerializer(serializers.ModelSerializer):
    """Full move serializer with nested image data for detail views"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Move
        fields = [
            'id', 'name', 'description', 'type', 'dmg_type',
            'dmg', 'accuracy', 'resource_cost', 'rarity',
            'lvl_learned', 'core_type_identity', 'track_type',
            'image', 'image_url', 'is_starter', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        """Return image battle_image path if available"""
        if obj.image and obj.image.battle_image:
            return obj.image.battle_image
        return None


class MoveListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views and nested serialization"""

    class Meta:
        model = Move
        fields = [
            'id', 'name', 'type', 'dmg_type', 'dmg',
            'accuracy', 'resource_cost', 'rarity', 'lvl_learned', 'is_starter', 'core_type_identity'
        ]


class MoveCreateSerializer(serializers.Serializer):
    """Serializer for creating curated moves (admin/seed data)"""
    name = serializers.CharField(max_length=120)
    description = serializers.CharField(allow_blank=True, default="")
    type = serializers.ChoiceField(choices=MOVE_FUNCTIONS)
    dmg_type = serializers.ChoiceField(choices=Move.DMG_TYPE_CHOICES)
    dmg = serializers.IntegerField(min_value=0)
    accuracy = serializers.FloatField(min_value=0.0, max_value=1.0)
    resource_cost = serializers.IntegerField(min_value=0)
    rarity = serializers.ChoiceField(choices=RARITIES)
    lvl_learned = serializers.IntegerField(default=0, min_value=0)
    core_type_identity = serializers.CharField(allow_blank=True, default="")
    track_type = serializers.CharField(allow_blank=True, default="")
    image_id = serializers.CharField(
        allow_blank=True, default="", required=False)
    is_starter = serializers.BooleanField(default=False)

    def validate_name(self, value):
        """Ensure move name is unique"""
        if Move.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"Move '{value}' already exists")
        return value

    def validate_type(self, value):
        """Validate move function is in allowed list"""
        if value not in MOVE_FUNCTIONS:
            raise serializers.ValidationError(
                f"Invalid move function. Must be one of: {MOVE_FUNCTIONS}"
            )
        return value

    def validate_dmg_type(self, value):
        """Validate damage type is in allowed list"""
        if value not in MOVE_DMG_TYPES:
            raise serializers.ValidationError(
                f"Invalid damage type. Must be one of: {MOVE_DMG_TYPES}"
            )
        return value

    def validate_core_type_identity(self, value):
        """Validate type identity is valid CORE_TYPE or empty (Generic)"""
        if value and value not in CORE_TYPES:
            raise serializers.ValidationError(
                f"Invalid core_type_identity. Must be one of: {CORE_TYPES} "
                f"or empty for Generic moves"
            )
        return value


class MoveGenerateSerializer(serializers.Serializer):
    """Serializer for generating procedural random moves"""
    rarity = serializers.ChoiceField(choices=RARITIES)
    move_type = serializers.ChoiceField(choices=MOVE_FUNCTIONS)
    dmg_type = serializers.ChoiceField(choices=Move.DMG_TYPE_CHOICES)


class MoveEquipSerializer(serializers.Serializer):
    """Serializer for equipping moves to cores"""
    move_id = serializers.UUIDField()
    slot = serializers.IntegerField(min_value=1)

    def validate_slot(self, value):
        """Basic slot validation (max validation happens in view with core context)"""
        if value < 1:
            raise serializers.ValidationError("Slot must be at least 1")
        return value


class MoveUnequipSerializer(serializers.Serializer):
    """Serializer for unequipping moves from cores"""
    slot = serializers.IntegerField(min_value=1)

    def validate_slot(self, value):
        """Basic slot validation"""
        if value < 1:
            raise serializers.ValidationError("Slot must be at least 1")
        return value
