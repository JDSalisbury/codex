# battle/models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from codex.models import TimestampedModel


# ============================================================================
# Battle Models
# ============================================================================

class Battle(TimestampedModel):
    """Main battle record tracking a complete combat session."""
    BATTLE_TYPE_CHOICES = [
        ("PVP", "Player vs Player"),
        ("PVE", "Player vs Environment"),
        ("MISSION", "Mission"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("ABANDONED", "Abandoned"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    operator_1 = models.ForeignKey(
        "codex.Operator",
        on_delete=models.CASCADE,
        related_name="battles_as_operator_1"
    )
    operator_2 = models.ForeignKey(
        "codex.Operator",
        on_delete=models.CASCADE,
        related_name="battles_as_operator_2",
        null=True,
        blank=True  # Null for PVE battles
    )

    battle_type = models.CharField(
        max_length=20,
        choices=BATTLE_TYPE_CHOICES,
        default="PVE"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    winner = models.ForeignKey(
        "codex.Operator",
        on_delete=models.SET_NULL,
        related_name="battles_won",
        null=True,
        blank=True
    )

    current_turn = models.PositiveIntegerField(default=0)
    rewards = models.JSONField(default=dict, blank=True)

    # Optional mission reference
    mission = models.ForeignKey(
        "Mission",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="battles"
    )

    def __str__(self):
        return f"Battle {self.id} - {self.battle_type} ({self.status})"


class BattleTeam(TimestampedModel):
    """One side's team state within a battle. Tracks resource pools."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    battle = models.ForeignKey(
        Battle,
        on_delete=models.CASCADE,
        related_name="teams"
    )
    operator = models.ForeignKey(
        "codex.Operator",
        on_delete=models.CASCADE,
        related_name="battle_teams"
    )

    # Shared team resource pools (filled by d8 rolls)
    energy_pool = models.PositiveIntegerField(default=0)
    physical_pool = models.PositiveIntegerField(default=0)

    # Which core is currently active (0, 1, or 2)
    active_core_index = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["battle", "operator"],
                name="uniq_battle_operator_team"
            ),
        ]

    def __str__(self):
        return f"Team {self.operator.call_sign} in Battle {self.battle_id}"


class BattleCoreState(TimestampedModel):
    """Snapshot of a Core's state during battle. Tracks HP and status."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    team = models.ForeignKey(
        BattleTeam,
        on_delete=models.CASCADE,
        related_name="core_states"
    )
    core = models.ForeignKey(
        "codex.Core",
        on_delete=models.CASCADE,
        related_name="battle_states"
    )

    # Position in the team lineup (0, 1, or 2)
    position = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )

    # Battle-specific HP tracking
    current_hp = models.PositiveIntegerField(default=0)
    max_hp = models.PositiveIntegerField(default=0)
    is_knocked_out = models.BooleanField(default=False)

    # Last dice roll for this core (1-8)
    last_dice_roll = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )

    # Status effects (JSON for flexibility)
    status_effects = models.JSONField(default=list, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team", "position"],
                name="uniq_team_position"
            ),
            models.UniqueConstraint(
                fields=["team", "core"],
                name="uniq_team_core"
            ),
        ]

    def __str__(self):
        return f"{self.core.name} (pos {self.position}) - {self.current_hp}/{self.max_hp} HP"


class BattleTurn(TimestampedModel):
    """Record of a single turn within a battle."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    battle = models.ForeignKey(
        Battle,
        on_delete=models.CASCADE,
        related_name="turns"
    )
    turn_number = models.PositiveIntegerField()

    acting_team = models.ForeignKey(
        BattleTeam,
        on_delete=models.CASCADE,
        related_name="turns_acted"
    )

    # JSON snapshots for replay/debugging
    state_before = models.JSONField(default=dict, blank=True)
    state_after = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["battle", "turn_number", "acting_team"],
                name="uniq_battle_turn_team"
            ),
        ]
        ordering = ["turn_number"]

    def __str__(self):
        return f"Turn {self.turn_number} - {self.acting_team.operator.call_sign}"


class BattleAction(TimestampedModel):
    """Individual action taken within a turn (move, switch, pass, reaction)."""
    ACTION_TYPE_CHOICES = [
        ("MOVE", "Move"),
        ("SWITCH", "Switch"),
        ("PASS", "Pass"),
        ("REACTION", "Reaction"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    turn = models.ForeignKey(
        BattleTurn,
        on_delete=models.CASCADE,
        related_name="actions"
    )

    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPE_CHOICES
    )

    # Optional move reference (for MOVE actions)
    move = models.ForeignKey(
        "codex.Move",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="battle_actions"
    )

    # Source and target cores for the action
    source_core = models.ForeignKey(
        BattleCoreState,
        on_delete=models.CASCADE,
        related_name="actions_as_source",
        null=True,
        blank=True
    )
    target_core = models.ForeignKey(
        BattleCoreState,
        on_delete=models.CASCADE,
        related_name="actions_as_target",
        null=True,
        blank=True
    )

    # Combat results
    damage_dealt = models.PositiveIntegerField(default=0)
    accuracy_check = models.BooleanField(null=True, blank=True)
    was_critical = models.BooleanField(default=False)

    # Resource costs paid
    energy_cost = models.PositiveIntegerField(default=0)
    physical_cost = models.PositiveIntegerField(default=0)

    # Order of action within the turn
    sequence = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sequence"]

    def __str__(self):
        action_desc = self.action_type
        if self.move:
            action_desc = f"{self.action_type}: {self.move.name}"
        return f"Action {self.sequence} - {action_desc}"


class DiceRoll(TimestampedModel):
    """Track d8 rolls and their allocation to resource pools."""
    ALLOCATION_CHOICES = [
        ("ENERGY", "Energy Pool"),
        ("PHYSICAL", "Physical Pool"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    turn = models.ForeignKey(
        BattleTurn,
        on_delete=models.CASCADE,
        related_name="dice_rolls"
    )
    core_state = models.ForeignKey(
        BattleCoreState,
        on_delete=models.CASCADE,
        related_name="dice_rolls"
    )

    # The actual d8 roll result (1-8)
    roll_value = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )

    # Where the roll was allocated
    allocated_to = models.CharField(
        max_length=20,
        choices=ALLOCATION_CHOICES,
        blank=True,
        default=""
    )

    def __str__(self):
        alloc = f" -> {self.allocated_to}" if self.allocated_to else " (unallocated)"
        return f"Roll {self.roll_value}{alloc}"


# ============================================================================
# Mission Models
# ============================================================================

class Mission(TimestampedModel):
    """PVE mission/contract definition with requirements and rewards."""
    DIFFICULTY_CHOICES = [
        ("EASY", "Easy"),
        ("MEDIUM", "Medium"),
        ("HARD", "Hard"),
        ("EXTREME", "Extreme"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default="EASY"
    )

    # Requirements to start the mission (level, core types, etc.)
    requirements = models.JSONField(default=dict, blank=True)

    # Rewards for completion (bits, exp, move_chance, etc.)
    rewards = models.JSONField(default=dict, blank=True)

    # Enemy team template for PVE generation
    enemy_config = models.JSONField(default=dict, blank=True)

    # Mission availability
    expires_at = models.DateTimeField(null=True, blank=True)
    is_repeatable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    # Zone/region grouping
    zone = models.CharField(max_length=60, blank=True, default="")

    # Ordering priority (lower = appears first)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "difficulty", "name"]

    def __str__(self):
        return f"{self.name} ({self.difficulty})"


class OperatorMission(TimestampedModel):
    """Tracks an Operator's progress/status for a specific mission."""
    STATUS_CHOICES = [
        ("AVAILABLE", "Available"),
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("EXPIRED", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    operator = models.ForeignKey(
        "codex.Operator",
        on_delete=models.CASCADE,
        related_name="missions"
    )
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name="operator_progress"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="AVAILABLE"
    )

    attempts = models.PositiveIntegerField(default=0)
    victories = models.PositiveIntegerField(default=0)

    completed_at = models.DateTimeField(null=True, blank=True)
    rewards_claimed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["operator", "mission"],
                name="uniq_operator_mission"
            ),
        ]

    def __str__(self):
        return f"{self.operator.call_sign} - {self.mission.name} ({self.status})"


# ============================================================================
# Mail Models
# ============================================================================

class Mail(TimestampedModel):
    """In-game notifications and messages with optional attachments."""
    MAIL_TYPE_CHOICES = [
        ("SYSTEM", "System"),
        ("REWARD", "Reward"),
        ("BATTLE_RESULT", "Battle Result"),
        ("MISSION_UPDATE", "Mission Update"),
        ("NPC", "NPC Message"),           # Story NPCs
        ("OPERATOR", "Operator Message"),  # Rival/ally operators
        ("CORP", "Corporation Message"),   # Company recruitment/messages
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    operator = models.ForeignKey(
        "codex.Operator",
        on_delete=models.CASCADE,
        related_name="mail"
    )

    sender_name = models.CharField(max_length=100, default="System")

    mail_type = models.CharField(
        max_length=20,
        choices=MAIL_TYPE_CHOICES,
        default="SYSTEM"
    )

    subject = models.CharField(max_length=200)
    body = models.TextField(blank=True, default="")

    # Claimable rewards/items (JSON for flexibility)
    attachments = models.JSONField(default=dict, blank=True)

    is_read = models.BooleanField(default=False)
    is_claimed = models.BooleanField(default=False)

    # Optional expiration
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Mail"

    def __str__(self):
        read_status = "Read" if self.is_read else "Unread"
        return f"[{read_status}] {self.subject}"


# ============================================================================
# Arena Models
# ============================================================================

class NPCOperator(TimestampedModel):
    """
    Static NPC opponent for arena battles.
    Admin-managed, shared across all players.
    """
    ARENA_RANK_CHOICES = [
        ("S", "S"),
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("E", "E"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    call_sign = models.CharField(max_length=120, unique=True)
    title = models.CharField(max_length=200, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    portrait_url = models.CharField(max_length=500, blank=True, default="")

    # Arena positioning
    arena_rank = models.CharField(
        max_length=2,
        choices=ARENA_RANK_CHOICES,
        default="E"
    )
    floor = models.PositiveIntegerField(default=1)

    # Difficulty scaling
    difficulty_rating = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    core_level_range = models.JSONField(default=dict, blank=True)

    # Battle outcomes - messages to send via Mail
    win_mail_subject = models.CharField(max_length=200, default="Victory Acknowledged")
    win_mail_body = models.TextField(blank=True, default="")
    lose_mail_subject = models.CharField(max_length=200, default="Defeat Recorded")
    lose_mail_body = models.TextField(blank=True, default="")

    # Rewards on defeat
    reward_bits = models.PositiveIntegerField(default=100)
    reward_exp = models.PositiveIntegerField(default=50)

    # Gatekeeper flags
    is_gate_boss = models.BooleanField(default=False)
    unlocks_rank = models.CharField(max_length=2, blank=True, default="")

    # Active flag for admin control
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["arena_rank", "floor"]
        constraints = [
            models.UniqueConstraint(
                fields=["arena_rank", "floor"],
                name="uniq_arena_rank_floor"
            )
        ]

    def __str__(self):
        return f"[{self.arena_rank}-{self.floor}] {self.call_sign}"


class NPCCore(TimestampedModel):
    """
    Pre-configured core belonging to an NPC operator.
    Stats are fixed, not generated dynamically.
    """
    RARITY_CHOICES = [
        ("Common", "Common"),
        ("Uncommon", "Uncommon"),
        ("Rare", "Rare"),
        ("Legendary", "Legendary"),
        ("Mythic", "Mythic"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    npc_operator = models.ForeignKey(
        NPCOperator,
        on_delete=models.CASCADE,
        related_name="cores"
    )

    # Core identity
    name = models.CharField(max_length=120)
    core_type = models.CharField(max_length=60, blank=True, default="")
    rarity = models.CharField(
        max_length=20,
        choices=RARITY_CHOICES,
        default="Common"
    )
    lvl = models.PositiveIntegerField(default=1)
    image_url = models.CharField(max_length=500, blank=True, default="")

    # Position in team (0, 1, 2)
    team_position = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(2)]
    )

    # Battle stats (flat values)
    hp = models.PositiveIntegerField(default=100)
    physical = models.PositiveIntegerField(default=10)
    energy = models.PositiveIntegerField(default=10)
    defense = models.PositiveIntegerField(default=10)
    shield = models.PositiveIntegerField(default=10)
    speed = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ["npc_operator", "team_position"]
        constraints = [
            models.UniqueConstraint(
                fields=["npc_operator", "team_position"],
                name="uniq_npc_core_position"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.npc_operator.call_sign})"


class NPCCoreEquippedMove(TimestampedModel):
    """
    Moves equipped to an NPC's core.
    References the shared Move model from codex app.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    npc_core = models.ForeignKey(
        NPCCore,
        on_delete=models.CASCADE,
        related_name="equipped_moves"
    )
    move = models.ForeignKey(
        "codex.Move",
        on_delete=models.CASCADE,
        related_name="npc_equipped_by"
    )
    slot = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["npc_core", "slot"],
                name="uniq_npc_core_slot"
            ),
            models.UniqueConstraint(
                fields=["npc_core", "move"],
                name="uniq_npc_core_move"
            )
        ]

    def __str__(self):
        return f"{self.npc_core.name}: {self.move.name} (slot {self.slot})"


class OperatorArenaProgress(TimestampedModel):
    """
    Tracks a player's progress through the arena.
    One record per operator.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    operator = models.OneToOneField(
        "codex.Operator",
        on_delete=models.CASCADE,
        related_name="arena_progress"
    )

    # Current highest unlocked rank
    current_rank = models.CharField(max_length=2, default="E")

    # Defeated NPCs (list of NPC UUIDs as strings)
    defeated_npcs = models.JSONField(default=list, blank=True)

    # Stats
    arena_wins = models.PositiveIntegerField(default=0)
    arena_losses = models.PositiveIntegerField(default=0)
    current_win_streak = models.PositiveIntegerField(default=0)
    best_win_streak = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.operator.call_sign} - Rank {self.current_rank}"
