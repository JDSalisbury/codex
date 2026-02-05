from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from codex.serializers.core import CoreSerializer, CoreGenerationRequestSerializer, CoreEquippedMoveSerializer
from .models import Operator, ImageAsset, Garage, Core, Scrapyard, Move
from codex.serializers.operator import OperatorSerializer
from codex.serializers.garage import GarageSerializer
from codex.serializers.scrapyard import ScrapyardSerializer
from codex.serializers.move import (
    MoveSerializer, MoveListSerializer, MoveCreateSerializer,
    MoveGenerateSerializer, MoveEquipSerializer, MoveUnequipSerializer
)
from codex.services.core_factory import generate_core, CoreGenRequest
from codex.services.scrapyard import decommission_core, recommission_core, get_move_shop_rotation
from codex.services.move_factory import (
    create_move, MoveCreateRequest, generate_random_move,
    equip_move_to_core, unequip_move_from_core, MoveEquipRequest
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class OperatorView(viewsets.ModelViewSet):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer


class GarageView(viewsets.ModelViewSet):
    queryset = Garage.objects.all()
    serializer_class = GarageSerializer
    filterset_fields = ['operator']

    @action(detail=True, methods=['get'], url_path='move-library')
    def move_library(self, request, pk=None):
        """
        Get all moves in this garage's library with availability status.
        GET /api/garages/{id}/move-library/

        Returns:
        {
            "moves": [
                {
                    "move": {...},
                    "copies_owned": 2,
                    "copies_equipped": 1,
                    "copies_available": 1,
                    "equipped_by": ["Core 1"]
                }
            ]
        }
        """
        from codex.models import GarageMoveLibrary, CoreEquippedMove
        from codex.serializers.move import MoveSerializer

        garage = self.get_object()

        library_entries = GarageMoveLibrary.objects.filter(
            garage=garage
        ).select_related('move').prefetch_related('move__image')

        library_data = []
        for entry in library_entries:
            # Get cores that have this move equipped
            equipped_cores = CoreEquippedMove.objects.filter(
                core__garage=garage,
                move=entry.move
            ).select_related('core').values_list('core__name', flat=True)

            library_data.append({
                "move": MoveSerializer(entry.move).data,
                "copies_owned": entry.copies_owned,
                "copies_equipped": len(equipped_cores),
                "copies_available": entry.copies_owned - len(equipped_cores),
                "equipped_by": list(equipped_cores)
            })

        return Response({"moves": library_data}, status=status.HTTP_200_OK)


class CoreView(viewsets.ModelViewSet):
    queryset = Core.objects.all()
    serializer_class = CoreSerializer
    filterset_fields = ['garage', 'decommed', 'rarity', 'type']

    @action(detail=False, methods=['post'], url_path='generate')
    @transaction.atomic
    def generate(self, request):
        """
        Generate a new core with random stats based on rarity and track.
        POST /api/cores/generate/
        Request body: {name, rarity, track, garage_id}
        """
        serializer = CoreGenerationRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        garage = validated_data['garage']
        price = validated_data['price']

        # Create CoreGenRequest for core_factory
        core_gen_request = CoreGenRequest(
            name=validated_data['name'],
            core_type="",  # Not used, randomly assigned in factory
            rarity=validated_data['rarity'],
            track=validated_data['track'],
            price=price
        )

        try:
            # Generate core using factory service
            core = generate_core(garage, core_gen_request)

            # Deduct bits from operator
            garage.operator.bits -= price
            garage.operator.save()

            # Return serialized core
            core_serializer = CoreSerializer(core)
            return Response(core_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Core generation failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='decommission')
    @transaction.atomic
    def decommission(self, request, pk=None):
        """
        Decommission a core (soft delete) and add to scrapyard.
        POST /api/cores/{id}/decommission/
        """
        core = self.get_object()

        if core.decommed:
            return Response(
                {"error": "Core is already decommissioned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create global scrapyard (MVP: single global scrapyard)
        scrapyard, _ = Scrapyard.objects.get_or_create(
            id='00000000-0000-0000-0000-000000000001'
        )

        try:
            decommission_core(core, scrapyard)
            return Response(
                {"message": f"Core '{core.name}' decommissioned successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Decommission failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='recommission')
    @transaction.atomic
    def recommission(self, request, pk=None):
        """
        Recommission a decommissioned core (restore to active).
        POST /api/cores/{id}/recommission/
        """
        core = self.get_object()

        if not core.decommed:
            return Response(
                {"error": "Core is not decommissioned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check garage capacity
        garage = core.garage
        if not garage.has_capacity():
            return Response(
                {"error": "Garage is at full capacity."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # MVP: free recommission, pass 0 for bits_cost
            recommission_core(core, operator_bits_cost=0)

            # Remove from scrapyard decommed_cores list
            scrapyard = Scrapyard.objects.filter(
                id='00000000-0000-0000-0000-000000000001'
            ).first()

            if scrapyard:
                scrapyard.decommed_cores = [
                    snapshot for snapshot in scrapyard.decommed_cores
                    if snapshot.get("core_id") != str(core.id)
                ]
                scrapyard.save(update_fields=["decommed_cores"])

            return Response(
                {"message": f"Core '{core.name}' recommissioned successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Recommission failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='equip-move')
    @transaction.atomic
    def equip_move(self, request, pk=None):
        """
        Equip a move from the core's pool to a specific slot.
        POST /api/cores/{id}/equip-move/
        Body: {move_id: uuid, slot: int}
        """
        core = self.get_object()
        serializer = MoveEquipSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            req = MoveEquipRequest(
                core_id=str(core.id),
                move_id=str(serializer.validated_data['move_id']),
                slot=serializer.validated_data['slot']
            )
            equipped = equip_move_to_core(req)

            response_serializer = CoreEquippedMoveSerializer(equipped)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='unequip-move')
    @transaction.atomic
    def unequip_move(self, request, pk=None):
        """
        Unequip a move from a specific slot.
        POST /api/cores/{id}/unequip-move/
        Body: {slot: int}
        """
        core = self.get_object()
        serializer = MoveUnequipSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            unequip_move_from_core(str(core.id), serializer.validated_data['slot'])
            return Response(
                {"message": f"Move unequipped from slot {serializer.validated_data['slot']}"},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'], url_path='available-moves')
    def available_moves(self, request, pk=None):
        """
        Returns all moves available to this core:
        - Garage library moves (shared, swappable)
        - Core-exclusive moves (starters, signatures)

        GET /api/cores/{id}/available-moves/
        """
        from codex.services.move_factory import get_garage_available_moves
        from codex.serializers.move import MoveSerializer

        core = self.get_object()

        # Get combined availability data
        available = get_garage_available_moves(
            str(core.garage.id),
            str(core.id)
        )

        # Format for frontend
        response_data = []
        for item in available:
            move_data = MoveSerializer(item['move']).data
            move_data['availability'] = {
                'source': item['source'],
                'can_equip': item.get('can_equip', False)
            }

            if item['source'] == 'garage_library':
                move_data['availability'].update({
                    'copies_owned': item['copies_owned'],
                    'copies_equipped': item['copies_equipped'],
                    'copies_available': item['copies_available']
                })
            else:  # core_exclusive
                move_data['availability'].update({
                    'is_starter': item.get('is_starter', False),
                    'is_signature': item.get('is_signature', False),
                    'is_equipped': item.get('is_equipped', False)
                })

            response_data.append(move_data)

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='equipped-moves')
    def equipped_moves(self, request, pk=None):
        """
        Get all equipped moves for this core.
        GET /api/cores/{id}/equipped-moves/
        """
        core = self.get_object()
        equipped = core.equipped_moves.through.objects.filter(core=core).select_related('move')
        serializer = CoreEquippedMoveSerializer(equipped, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='purchase-move')
    @transaction.atomic
    def purchase_move(self, request, pk=None):
        """
        Purchase a move from the shop and add it to the GARAGE library.
        POST /api/cores/{id}/purchase-move/
        Body: {move_id: uuid}

        Note: Purchases now go to garage library (shared), not core-specific.
        """
        from codex.constants import RARITY_PRICES
        from codex.services.move_factory import add_move_to_garage_library

        core = self.get_object()
        move_id = request.data.get('move_id')

        if not move_id:
            return Response(
                {"error": "move_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            move = Move.objects.get(id=move_id)
        except Move.DoesNotExist:
            return Response(
                {"error": "Move not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if move is starter (shouldn't be purchasable)
        if move.is_starter:
            return Response(
                {"error": "Starter moves cannot be purchased"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if signature move (non-purchasable, core-exclusive)
        if move.is_signature:
            return Response(
                {"error": "Signature moves cannot be purchased"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get price based on rarity
        price = RARITY_PRICES.get(move.rarity, 100)

        # Check if operator has enough bits
        operator = core.garage.operator
        if operator.bits < price:
            return Response(
                {"error": f"Insufficient credits. Need {price}, have {operator.bits}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Add to garage library (handles copy limit checks)
            library_entry = add_move_to_garage_library(
                str(core.garage.id),
                str(move.id)
            )

            # Deduct bits
            operator.bits -= price
            operator.save(update_fields=['bits'])

            return Response(
                {
                    "message": f"Purchased {move.name} for {price} credits",
                    "move_name": move.name,
                    "copies_owned": library_entry.copies_owned,
                    "remaining_bits": operator.bits,
                    "move": MoveListSerializer(move).data
                },
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            # Catch validation errors (e.g., max copies already owned)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Purchase failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MoveView(viewsets.ModelViewSet):
    """
    ViewSet for Move CRUD operations.
    List/Detail: Public for browsing available moves
    Create/Update/Delete: Admin only (or via custom actions)
    """
    queryset = Move.objects.all().select_related('image')
    serializer_class = MoveSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'dmg_type', 'rarity', 'is_starter', 'track_type']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'dmg', 'resource_cost', 'rarity', 'lvl_learned']
    ordering = ['name']  # Default ordering

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return MoveListSerializer
        elif self.action in ['create_move', 'generate_random']:
            return MoveCreateSerializer
        return MoveSerializer

    @action(detail=False, methods=['post'], url_path='create-move')
    @transaction.atomic
    def create_move(self, request):
        """
        Create a new curated move template with exact stats.
        POST /api/moves/create-move/
        Body: {name, description, type, dmg_type, dmg, accuracy, resource_cost, rarity, ...}
        """
        serializer = MoveCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            move_req = MoveCreateRequest(**serializer.validated_data)
            move = create_move(move_req)

            response_serializer = MoveSerializer(move)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='generate-random')
    @transaction.atomic
    def generate_random(self, request):
        """
        Generate a procedural move with random stats within rarity ranges.
        POST /api/moves/generate-random/
        Body: {rarity, move_type, dmg_type}
        """
        serializer = MoveGenerateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            move = generate_random_move(
                rarity=serializer.validated_data['rarity'],
                move_type=serializer.validated_data['move_type'],
                dmg_type=serializer.validated_data['dmg_type']
            )

            response_serializer = MoveSerializer(move)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ScrapyardView(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Scrapyard - read-only for MVP.
    Supports fetching scrapyard data and decommissioned cores.
    """
    queryset = Scrapyard.objects.all()
    serializer_class = ScrapyardSerializer

    @action(detail=False, methods=['get'], url_path='decommissioned-cores')
    def decommissioned_cores(self, request):
        """
        Get all decommissioned cores from the global scrapyard.
        GET /api/scrapyard/decommissioned-cores/
        """
        # Get or create global scrapyard
        scrapyard, _ = Scrapyard.objects.get_or_create(
            id='00000000-0000-0000-0000-000000000001'
        )

        # Get all decommissioned cores with full details
        decommed_core_ids = [
            snapshot.get("core_id")
            for snapshot in scrapyard.decommed_cores
            if snapshot.get("core_id")
        ]

        # Fetch actual Core objects
        cores = Core.objects.filter(
            id__in=decommed_core_ids,
            decommed=True
        ).select_related('battle_info', 'upgrade_info')

        # Serialize the cores
        serializer = CoreSerializer(cores, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='move-shop')
    def move_shop(self, request):
        """
        Get available moves for purchase in the Scrapyard Move Shop.
        GET /api/scrapyard/move-shop/
        Returns all non-starter moves with pricing.
        """
        shop_moves = get_move_shop_rotation()
        return Response(shop_moves, status=status.HTTP_200_OK)
