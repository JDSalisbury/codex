# battle/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Mail, NPCOperator, OperatorArenaProgress, Battle
from .serializers import (
    MailListSerializer, MailDetailSerializer,
    NPCOperatorListSerializer, NPCOperatorDetailSerializer,
    OperatorArenaProgressSerializer
)
from .services import battle_engine


class MailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Mail operations.
    Supports listing, filtering, and marking mail as read.
    """
    serializer_class = MailDetailSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['operator', 'mail_type', 'sender_name', 'is_read']
    ordering_fields = ['is_read', 'created_at']
    ordering = ['is_read', '-created_at']  # Unread first, then by date

    def get_queryset(self):
        """
        Return mail filtered by operator if provided.
        Orders by is_read (unread first) then by created_at descending.
        """
        queryset = Mail.objects.all()

        # Filter by operator if provided
        operator_id = self.request.query_params.get('operator')
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)

        return queryset.order_by('is_read', '-created_at')

    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == 'list':
            return MailListSerializer
        return MailDetailSerializer

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """
        Mark a mail as read.
        POST /battle/mail/{id}/mark-read/
        """
        mail = self.get_object()
        mail.is_read = True
        mail.save(update_fields=['is_read'])
        return Response({'status': 'marked as read'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """
        Get the count of unread mail for an operator.
        GET /battle/mail/unread-count/?operator={operator_id}
        """
        operator_id = request.query_params.get('operator')
        if not operator_id:
            return Response(
                {'error': 'operator query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        count = Mail.objects.filter(
            operator_id=operator_id,
            is_read=False
        ).count()

        return Response({'unread_count': count}, status=status.HTTP_200_OK)


class ArenaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Arena NPC operators.
    Supports listing by rank and viewing individual NPC details.
    """
    queryset = NPCOperator.objects.filter(is_active=True).prefetch_related(
        'cores', 'cores__equipped_moves', 'cores__equipped_moves__move'
    )
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['arena_rank', 'is_gate_boss']
    ordering_fields = ['arena_rank', 'floor', 'difficulty_rating']
    ordering = ['arena_rank', '-floor']  # Show highest floor (starting point) first

    def get_serializer_class(self):
        if self.action == 'list':
            return NPCOperatorListSerializer
        return NPCOperatorDetailSerializer

    @action(detail=False, methods=['get'], url_path='by-rank/(?P<rank>[A-Z])')
    def by_rank(self, request, rank=None):
        """
        Get all NPCs for a specific arena rank.
        GET /battle/arena/by-rank/E/?operator={operator_id}
        """
        if rank not in ['S', 'A', 'B', 'C', 'D', 'E']:
            return Response(
                {'error': 'Invalid rank. Must be S, A, B, C, D, or E'},
                status=status.HTTP_400_BAD_REQUEST
            )

        npcs = self.get_queryset().filter(arena_rank=rank)
        serializer = NPCOperatorListSerializer(
            npcs, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='progress')
    def progress(self, request):
        """
        Get the player's arena progress.
        GET /battle/arena/progress/?operator={operator_id}
        """
        operator_id = request.query_params.get('operator')
        if not operator_id:
            return Response(
                {'error': 'operator query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        progress, created = OperatorArenaProgress.objects.get_or_create(
            operator_id=operator_id,
            defaults={'current_rank': 'E'}
        )

        serializer = OperatorArenaProgressSerializer(progress)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='challenge')
    def challenge(self, request, pk=None):
        """
        Challenge an NPC to battle (placeholder for future battle system).
        POST /battle/arena/{npc_id}/challenge/
        Body: {operator_id, outcome: "win"|"lose"}

        For MVP: Just record outcome and send mail.
        """
        from codex.models import Operator

        npc = self.get_object()
        operator_id = request.data.get('operator_id')
        outcome = request.data.get('outcome')

        if not operator_id:
            return Response(
                {'error': 'operator_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if outcome not in ['win', 'lose']:
            return Response(
                {'error': 'outcome must be "win" or "lose"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            operator = Operator.objects.get(id=operator_id)
        except Operator.DoesNotExist:
            return Response(
                {'error': 'Operator not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get or create arena progress
        progress, _ = OperatorArenaProgress.objects.get_or_create(
            operator=operator,
            defaults={'current_rank': 'E'}
        )

        # Process outcome
        if outcome == 'win':
            progress.arena_wins += 1
            progress.current_win_streak += 1
            progress.best_win_streak = max(
                progress.best_win_streak,
                progress.current_win_streak
            )

            # Add to defeated list if not already
            if str(npc.id) not in progress.defeated_npcs:
                progress.defeated_npcs.append(str(npc.id))

            # Check if this unlocks next rank
            if npc.is_gate_boss and npc.unlocks_rank:
                rank_order = {'E': 0, 'D': 1, 'C': 2, 'B': 3, 'A': 4, 'S': 5}
                if rank_order.get(npc.unlocks_rank, 0) > rank_order.get(progress.current_rank, 0):
                    progress.current_rank = npc.unlocks_rank

            # Award rewards
            operator.bits += npc.reward_bits
            operator.save(update_fields=['bits'])

            # Send win mail
            Mail.objects.create(
                operator=operator,
                sender_name=npc.call_sign,
                mail_type='OPERATOR',
                subject=npc.win_mail_subject,
                body=npc.win_mail_body,
                attachments={'bits': npc.reward_bits, 'exp': npc.reward_exp}
            )

            message = f"Victory! Defeated {npc.call_sign}. Earned {npc.reward_bits} bits."

        else:  # lose
            progress.arena_losses += 1
            progress.current_win_streak = 0

            # Send lose mail
            Mail.objects.create(
                operator=operator,
                sender_name=npc.call_sign,
                mail_type='OPERATOR',
                subject=npc.lose_mail_subject,
                body=npc.lose_mail_body
            )

            message = f"Defeat. {npc.call_sign} was too strong this time."

        progress.save()

        return Response({
            'message': message,
            'progress': OperatorArenaProgressSerializer(progress).data
        })

    @action(detail=True, methods=['post'], url_path='start-battle')
    def start_battle(self, request, pk=None):
        """
        Start a real battle against an NPC.
        POST /battle/arena/{npc_id}/start-battle/
        Body: {operator_id: uuid}

        Returns {battle_id: uuid} for websocket connection.
        """
        npc = self.get_object()
        operator_id = request.data.get('operator_id')

        if not operator_id:
            return Response(
                {'error': 'operator_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            battle = battle_engine.create_battle_from_npc(operator_id, str(npc.id))
            return Response({
                'battle_id': str(battle.id),
                'message': f'Battle initiated against {npc.call_sign}',
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
