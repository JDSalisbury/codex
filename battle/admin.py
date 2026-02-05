# battle/admin.py
from django.contrib import admin
from battle.models import (
    Battle,
    BattleTeam,
    BattleCoreState,
    BattleTurn,
    BattleAction,
    DiceRoll,
    Mission,
    OperatorMission,
    Mail,
    NPCOperator,
    NPCCore,
    NPCCoreEquippedMove,
    OperatorArenaProgress,
)


class BattleTeamInline(admin.TabularInline):
    model = BattleTeam
    extra = 0
    readonly_fields = ("id", "created_at")


class BattleTurnInline(admin.TabularInline):
    model = BattleTurn
    extra = 0
    readonly_fields = ("id", "created_at")


@admin.register(Battle)
class BattleAdmin(admin.ModelAdmin):
    list_display = ("id", "battle_type", "status", "operator_1", "operator_2", "winner", "current_turn", "created_at")
    list_filter = ("battle_type", "status", "created_at")
    search_fields = ("id", "operator_1__call_sign", "operator_2__call_sign")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [BattleTeamInline, BattleTurnInline]


class BattleCoreStateInline(admin.TabularInline):
    model = BattleCoreState
    extra = 0
    readonly_fields = ("id",)


@admin.register(BattleTeam)
class BattleTeamAdmin(admin.ModelAdmin):
    list_display = ("id", "battle", "operator", "energy_pool", "physical_pool", "active_core_index")
    list_filter = ("battle__status",)
    search_fields = ("operator__call_sign",)
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [BattleCoreStateInline]


@admin.register(BattleCoreState)
class BattleCoreStateAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "core", "position", "current_hp", "max_hp", "is_knocked_out")
    list_filter = ("is_knocked_out",)
    search_fields = ("core__name",)
    readonly_fields = ("id", "created_at", "updated_at")


class BattleActionInline(admin.TabularInline):
    model = BattleAction
    extra = 0
    readonly_fields = ("id",)


class DiceRollInline(admin.TabularInline):
    model = DiceRoll
    extra = 0
    readonly_fields = ("id",)


@admin.register(BattleTurn)
class BattleTurnAdmin(admin.ModelAdmin):
    list_display = ("id", "battle", "turn_number", "acting_team", "created_at")
    list_filter = ("battle__status",)
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [BattleActionInline, DiceRollInline]


@admin.register(BattleAction)
class BattleActionAdmin(admin.ModelAdmin):
    list_display = ("id", "turn", "action_type", "move", "damage_dealt", "sequence")
    list_filter = ("action_type",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(DiceRoll)
class DiceRollAdmin(admin.ModelAdmin):
    list_display = ("id", "turn", "core_state", "roll_value", "allocated_to")
    list_filter = ("allocated_to",)
    readonly_fields = ("id", "created_at", "updated_at")


class OperatorMissionInline(admin.TabularInline):
    model = OperatorMission
    extra = 0
    readonly_fields = ("id", "created_at")


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "difficulty", "zone", "is_active", "is_repeatable", "expires_at")
    list_filter = ("difficulty", "is_active", "is_repeatable", "zone")
    search_fields = ("name", "description")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [OperatorMissionInline]


@admin.register(OperatorMission)
class OperatorMissionAdmin(admin.ModelAdmin):
    list_display = ("id", "operator", "mission", "status", "attempts", "victories", "rewards_claimed")
    list_filter = ("status", "rewards_claimed")
    search_fields = ("operator__call_sign", "mission__name")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ("id", "operator", "sender_name", "mail_type", "subject", "is_read", "is_claimed", "expires_at", "created_at")
    list_filter = ("mail_type", "is_read", "is_claimed")
    search_fields = ("operator__call_sign", "subject", "body", "sender_name")
    readonly_fields = ("id", "created_at", "updated_at")


# ============================================================================
# Arena Admin
# ============================================================================

class NPCCoreEquippedMoveInline(admin.TabularInline):
    """Inline for managing equipped moves on NPC cores."""
    model = NPCCoreEquippedMove
    extra = 1
    autocomplete_fields = ['move']
    ordering = ['slot']


class NPCCoreInline(admin.StackedInline):
    """Inline for managing NPC cores within operator admin."""
    model = NPCCore
    extra = 0
    max_num = 3
    ordering = ['team_position']
    fieldsets = (
        (None, {
            'fields': ('name', 'team_position', 'core_type', 'rarity', 'lvl', 'image_url')
        }),
        ('Battle Stats', {
            'fields': (('hp', 'speed'), ('physical', 'energy'), ('defense', 'shield')),
            'classes': ('collapse',)
        }),
    )


@admin.register(NPCOperator)
class NPCOperatorAdmin(admin.ModelAdmin):
    """Admin for managing NPC Arena opponents."""
    list_display = (
        'call_sign', 'arena_rank', 'floor', 'difficulty_rating',
        'is_gate_boss', 'is_active', 'reward_bits'
    )
    list_filter = ('arena_rank', 'is_gate_boss', 'is_active')
    search_fields = ('call_sign', 'title', 'bio')
    ordering = ['arena_rank', 'floor']

    fieldsets = (
        ('Identity', {
            'fields': ('call_sign', 'title', 'bio', 'portrait_url')
        }),
        ('Arena Position', {
            'fields': (('arena_rank', 'floor'), 'difficulty_rating', 'core_level_range')
        }),
        ('Gate Boss Settings', {
            'fields': (('is_gate_boss', 'unlocks_rank'),),
            'classes': ('collapse',)
        }),
        ('Rewards', {
            'fields': (('reward_bits', 'reward_exp'),)
        }),
        ('Win Mail', {
            'fields': ('win_mail_subject', 'win_mail_body'),
            'classes': ('collapse',)
        }),
        ('Lose Mail', {
            'fields': ('lose_mail_subject', 'lose_mail_body'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    inlines = [NPCCoreInline]

    def get_inline_instances(self, request, obj=None):
        """Only show core inlines when editing existing NPC."""
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(NPCCore)
class NPCCoreAdmin(admin.ModelAdmin):
    """Direct admin for NPC Cores (useful for bulk editing)."""
    list_display = (
        'name', 'npc_operator', 'team_position',
        'core_type', 'rarity', 'lvl', 'hp', 'speed'
    )
    list_filter = ('npc_operator__arena_rank', 'rarity', 'core_type')
    search_fields = ('name', 'npc_operator__call_sign')
    ordering = ['npc_operator__arena_rank', 'npc_operator__floor', 'team_position']
    inlines = [NPCCoreEquippedMoveInline]

    fieldsets = (
        (None, {
            'fields': ('npc_operator', 'name', 'team_position', 'image_url')
        }),
        ('Type & Level', {
            'fields': (('core_type', 'rarity', 'lvl'),)
        }),
        ('Battle Stats', {
            'fields': (('hp', 'speed'), ('physical', 'energy'), ('defense', 'shield'))
        }),
    )


@admin.register(NPCCoreEquippedMove)
class NPCCoreEquippedMoveAdmin(admin.ModelAdmin):
    """Direct admin for NPC equipped moves."""
    list_display = ('npc_core', 'move', 'slot')
    list_filter = ('npc_core__npc_operator__arena_rank',)
    search_fields = ('npc_core__name', 'move__name')
    autocomplete_fields = ['move']


@admin.register(OperatorArenaProgress)
class OperatorArenaProgressAdmin(admin.ModelAdmin):
    """Admin for viewing/editing player arena progress."""
    list_display = (
        'operator', 'current_rank', 'arena_wins',
        'arena_losses', 'current_win_streak', 'best_win_streak'
    )
    list_filter = ('current_rank',)
    search_fields = ('operator__call_sign',)
    readonly_fields = ('id', 'created_at', 'updated_at')
