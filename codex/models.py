# codex/models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from codex import constants


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Operator(TimestampedModel):
    RANKS = ('S', 'A', 'B', 'C', 'D', 'E', 'F')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    call_sign = models.CharField(max_length=120, default="000")
    rank = models.CharField(max_length=60, blank=True, choices=[
                            (r, r) for r in RANKS], default='F')

    lvl = models.PositiveIntegerField(default=0)

    wins = models.PositiveIntegerField(default=0)
    loses = models.PositiveIntegerField(default=0)
    bits = models.PositiveIntegerField(default=0)
    premium = models.PositiveIntegerField(default=0)

    # future hooks
    # or M2M via ZoneProgress later
    zones = models.JSONField(default=list, blank=True)
    # or M2M via ChoiceLog later
    choices = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return f"Operator {self.id} (lvl {self.lvl})"


class ImageAsset(TimestampedModel):
    """
    Reusable art + palette variants + animation references.
    Store paths/URLs/ids as strings; integrate with S3 later if desired.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    source_id = models.CharField(max_length=128, unique=True)
    main = models.BooleanField(default=False)

    r = models.PositiveIntegerField(default=255, validators=[
                                    MinValueValidator(0), MaxValueValidator(255)])
    g = models.PositiveIntegerField(default=255, validators=[
                                    MinValueValidator(0), MaxValueValidator(255)])
    b = models.PositiveIntegerField(default=255, validators=[
                                    MinValueValidator(0), MaxValueValidator(255)])

    battle_image = models.CharField(max_length=255, blank=True, default="")
    battle_animation = models.JSONField(default=list, blank=True)
    dmg_animation = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return self.source_id


class Garage(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operator = models.OneToOneField(
        Operator, on_delete=models.CASCADE, related_name="garage")

    bay_doors = models.PositiveIntegerField(default=3)  # capacity
    # MVP: store 3-core team loadouts as IDs
    core_loadouts = models.JSONField(default=list, blank=True)

    # Shared move library for all cores in this garage
    move_library = models.ManyToManyField(
        'Move',
        through='GarageMoveLibrary',
        related_name="garages_owned",
        blank=True
    )

    def __str__(self) -> str:
        return f"Garage {self.id} (bay_doors={self.bay_doors})"

    @property
    def capacity(self) -> int:
        return self.bay_doors

    def has_capacity(self) -> bool:
        return self.cores.filter(decommed=False).count() < self.capacity


class GarageMoveLibrary(TimestampedModel):
    """
    Through table for Garage move library.
    Tracks shared moves and enforces copy limits.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE)
    move = models.ForeignKey('Move', on_delete=models.CASCADE)
    copies_owned = models.PositiveIntegerField(default=1)  # Track inventory (max 2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["garage", "move"],
                name="uniq_garage_move"
            ),
            models.CheckConstraint(
                condition=models.Q(copies_owned__lte=2),
                name="max_2_copies"
            ),
        ]
        indexes = [
            models.Index(fields=['garage', 'move']),
        ]

    def __str__(self):
        return f"{self.garage.operator.call_sign} - {self.move.name} (x{self.copies_owned})"


def list_to_choices(options: list[str]) -> list[tuple[str, str]]:
    return [(opt, opt) for opt in options]


class Move(TimestampedModel):
    DMG_TYPE_ENERGY = "ENERGY"
    DMG_TYPE_PHYSICAL = "PHYSICAL"
    DMG_TYPE_CHOICES = [
        (DMG_TYPE_ENERGY, "Energy Ammo"),
        (DMG_TYPE_PHYSICAL, "Physical Ammo"),
    ]

    CORE_TYPE_CHOICES = list_to_choices(constants.CORE_TYPES)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True, default="")
    # Attack/Defense/Reaction/etc.
    type = models.CharField(max_length=60, blank=True, default="")

    dmg_type = models.CharField(max_length=16, choices=DMG_TYPE_CHOICES)
    dmg = models.IntegerField(default=0)

    accuracy = models.FloatField(default=1.0, validators=[
                                 MinValueValidator(0.0), MaxValueValidator(1.0)])
    resource_cost = models.PositiveIntegerField(default=0)

    lvl_learned = models.PositiveIntegerField(default=0)

    # "Commander identity" / typing rules live here
    # e.g. "Defender", "Pyro", etc.
    core_type_identity = models.CharField(
        max_length=60, blank=True, default="", choices=CORE_TYPE_CHOICES)

    # track tags: "fortitude", "control", "resource", "physical_bias"
    track_type = models.CharField(max_length=60, blank=True, default="")

    # Rarity tiers (shared with Core model)
    RARITY_CHOICES = [
        ("Common", "Common"),
        ("Uncommon", "Uncommon"),
        ("Rare", "Rare"),
        ("Legendary", "Legendary"),
        ("Mythic", "Mythic"),
    ]
    rarity = models.CharField(
        max_length=20, choices=RARITY_CHOICES, default="Common")
    is_starter = models.BooleanField(default=False)
    is_signature = models.BooleanField(default=False)  # Ultra-rare core-exclusive moves

    image = models.ForeignKey(
        ImageAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="moves")

    def __str__(self) -> str:
        return self.name


class Equipment(TimestampedModel):
    """
    Equipment can be normal gear or a Move-as-item (is_move).
    MVP: keep bonuses as JSON.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True, default="")
    # armor, mod, chip, etc.
    type = models.CharField(max_length=60, blank=True, default="")

    equipped = models.BooleanField(default=False)
    bonuses = models.JSONField(default=list, blank=True)

    buy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sell_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    rarity = models.CharField(max_length=30, blank=True, default="Common")

    image = models.ForeignKey(ImageAsset, null=True, blank=True,
                              on_delete=models.SET_NULL, related_name="equipment")

    is_move = models.BooleanField(default=False)
    move = models.ForeignKey(Move, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="as_equipment")

    def __str__(self) -> str:
        return self.name


# TODO: Create core on garage creation -- initial core + default moves
class Core(TimestampedModel):
    RARITY_CHOICES = [
        ("Common", "Common"),
        ("Uncommon", "Uncommon"),
        ("Rare", "Rare"),
        ("Legendary", "Legendary"),
        ("Mythic", "Mythic"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    garage = models.ForeignKey(
        Garage, on_delete=models.CASCADE, related_name="cores")

    name = models.CharField(max_length=120)
    image = models.ForeignKey(
        ImageAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="cores")
    # MVP: Direct image URL storage (until we implement full ImageAsset system)
    image_url = models.CharField(max_length=500, blank=True, default="")

    # typing / identity
    type = models.CharField(max_length=60, blank=True, default="")
    rarity = models.CharField(
        max_length=20, choices=RARITY_CHOICES, default="Common")

    lvl = models.PositiveIntegerField(default=0)
    decommed = models.BooleanField(default=False)
    price = models.PositiveIntegerField(default=0)

    # Global move pool a Core can learn/use
    moves_pool = models.ManyToManyField(
        Move, blank=True, related_name="cores_with_access")

    # Equipped moves with ordering/slots
    equipped_moves = models.ManyToManyField(
        Move, through="CoreEquippedMove", related_name="equipped_by_cores")

    def __str__(self) -> str:
        return f"{self.name} ({self.rarity}) - {self.id}"


class CoreBattleInfo(TimestampedModel):
    core = models.OneToOneField(
        Core, on_delete=models.CASCADE, related_name="battle_info")

    hp = models.PositiveIntegerField(default=0)
    physical = models.PositiveIntegerField(default=0)
    energy = models.PositiveIntegerField(default=0)
    defense = models.PositiveIntegerField(default=0)
    shield = models.PositiveIntegerField(default=0)
    speed = models.PositiveIntegerField(default=0)

    equip_slots = models.PositiveIntegerField(default=4)

    def __str__(self) -> str:
        return f"BattleInfo({self.core.name})"


class CoreUpgradeInfo(TimestampedModel):
    core = models.OneToOneField(
        Core, on_delete=models.CASCADE, related_name="upgrade_info")

    exp = models.PositiveIntegerField(default=0)
    next_lvl = models.PositiveIntegerField(default=0)
    upgradeable = models.BooleanField(default=True)

    # Track definitions + logs are JSON until we formalize them
    tracks = models.JSONField(default=list, blank=True)
    lvl_logs = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return f"UpgradeInfo({self.core.name})"


class CoreEquippedMove(TimestampedModel):
    """
    Slot-based equip table. Guarantees:
    - No duplicate move equipped per core
    - Slot numbers are unique per core
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    core = models.ForeignKey(Core, on_delete=models.CASCADE)
    move = models.ForeignKey(Move, on_delete=models.CASCADE)

    slot = models.PositiveIntegerField(default=1)  # 1..equip_slots

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["core", "move"], name="uniq_core_move"),
            models.UniqueConstraint(
                fields=["core", "slot"], name="uniq_core_slot"),
        ]

    def __str__(self) -> str:
        return f"{self.core.name}: {self.move.name} (slot {self.slot})"


class Scrapyard(TimestampedModel):
    """
    Global storefront/rotation + logs.
    If you later want per-operator scrapyards, add operator FK.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    items_for_sale = models.JSONField(default=list, blank=True)
    bundles = models.JSONField(default=list, blank=True)
    weekly_deal = models.JSONField(default=dict, blank=True)
    purchase_logs = models.JSONField(default=list, blank=True)

    # Store decommed core IDs or snapshots; MVP uses snapshot list
    decommed_cores = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return f"Scrapyard {self.id}"
