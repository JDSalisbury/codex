# battle/serializers.py
from rest_framework import serializers
from .models import Mail, NPCOperator, NPCCore, NPCCoreEquippedMove, OperatorArenaProgress
from codex.serializers.move import MoveListSerializer


class MailListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for mail list view."""

    class Meta:
        model = Mail
        fields = [
            'id',
            'sender_name',
            'mail_type',
            'subject',
            'is_read',
            'created_at',
        ]


class MailDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for individual mail view."""

    class Meta:
        model = Mail
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'operator']


class MailMarkReadSerializer(serializers.Serializer):
    """Serializer for marking mail as read - no input needed."""
    pass


# ============================================================================
# Arena Serializers
# ============================================================================

class NPCCoreEquippedMoveSerializer(serializers.ModelSerializer):
    """Serialize equipped moves on NPC cores."""
    move = MoveListSerializer(read_only=True)

    class Meta:
        model = NPCCoreEquippedMove
        fields = ['id', 'move', 'slot']


class NPCCoreSerializer(serializers.ModelSerializer):
    """Serialize NPC cores with equipped moves."""
    equipped_moves = NPCCoreEquippedMoveSerializer(many=True, read_only=True)

    class Meta:
        model = NPCCore
        fields = [
            'id', 'name', 'core_type', 'rarity', 'lvl', 'image_url',
            'team_position', 'hp', 'physical', 'energy',
            'defense', 'shield', 'speed', 'equipped_moves'
        ]


class NPCCoreSummarySerializer(serializers.ModelSerializer):
    """Lightweight core serializer for list views (abridged card view)."""

    class Meta:
        model = NPCCore
        fields = ['id', 'name', 'core_type', 'rarity', 'lvl', 'image_url', 'team_position']


class NPCOperatorListSerializer(serializers.ModelSerializer):
    """
    List view serializer - shows operator card with abridged core info.
    For the arena grid display.
    """
    cores = NPCCoreSummarySerializer(many=True, read_only=True)
    is_defeated = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = NPCOperator
        fields = [
            'id', 'call_sign', 'title', 'portrait_url',
            'arena_rank', 'floor', 'difficulty_rating',
            'is_gate_boss', 'reward_bits', 'cores', 'is_defeated', 'is_locked'
        ]

    def get_is_defeated(self, obj):
        """Check if requesting operator has defeated this NPC."""
        request = self.context.get('request')
        if not request:
            return False

        operator_id = request.query_params.get('operator')
        if not operator_id:
            return False

        try:
            progress = OperatorArenaProgress.objects.get(operator_id=operator_id)
            return str(obj.id) in progress.defeated_npcs
        except OperatorArenaProgress.DoesNotExist:
            return False

    def get_is_locked(self, obj):
        """Check if this NPC is locked (requires defeating gate boss)."""
        request = self.context.get('request')
        if not request:
            return obj.arena_rank != 'E'

        operator_id = request.query_params.get('operator')
        if not operator_id:
            return obj.arena_rank != 'E'

        try:
            progress = OperatorArenaProgress.objects.get(operator_id=operator_id)
            rank_order = {'E': 0, 'D': 1, 'C': 2, 'B': 3, 'A': 4, 'S': 5}
            return rank_order.get(obj.arena_rank, 0) > rank_order.get(progress.current_rank, 0)
        except OperatorArenaProgress.DoesNotExist:
            return obj.arena_rank != 'E'


class NPCOperatorDetailSerializer(serializers.ModelSerializer):
    """
    Detail view serializer - full NPC info with complete core data.
    For the expanded card modal.
    """
    cores = NPCCoreSerializer(many=True, read_only=True)
    is_defeated = serializers.SerializerMethodField()

    class Meta:
        model = NPCOperator
        fields = [
            'id', 'call_sign', 'title', 'bio', 'portrait_url',
            'arena_rank', 'floor', 'difficulty_rating',
            'core_level_range', 'is_gate_boss', 'unlocks_rank',
            'reward_bits', 'reward_exp', 'cores', 'is_defeated'
        ]

    def get_is_defeated(self, obj):
        request = self.context.get('request')
        if not request:
            return False

        operator_id = request.query_params.get('operator')
        if not operator_id:
            return False

        try:
            progress = OperatorArenaProgress.objects.get(operator_id=operator_id)
            return str(obj.id) in progress.defeated_npcs
        except OperatorArenaProgress.DoesNotExist:
            return False


class OperatorArenaProgressSerializer(serializers.ModelSerializer):
    """Serialize player's arena progress."""

    class Meta:
        model = OperatorArenaProgress
        fields = [
            'id', 'current_rank', 'defeated_npcs',
            'arena_wins', 'arena_losses',
            'current_win_streak', 'best_win_streak'
        ]
        read_only_fields = ['id']
