# battle/consumers.py
"""
WebSocket consumer for real-time battle communication.
"""
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

from battle.models import Battle, OperatorArenaProgress, Mail, NPCOperator
from battle.services import battle_engine, npc_ai
from codex.models import Operator


class BattleConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer handling real-time battle communication.
    """

    async def connect(self):
        """Handle websocket connection."""
        self.battle_id = self.scope['url_route']['kwargs']['battle_id']
        self.battle_group_name = f'battle_{self.battle_id}'

        # Join battle group
        await self.channel_layer.group_add(
            self.battle_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial connection confirmation
        await self.send_json({
            'type': 'connection_established',
            'battle_id': self.battle_id,
        })

    async def disconnect(self, close_code):
        """Handle websocket disconnection."""
        await self.channel_layer.group_discard(
            self.battle_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        """Handle incoming JSON messages."""
        message_type = content.get('type')

        handlers = {
            'battle_init': self.handle_battle_init,
            'action': self.handle_player_action,
            'dice_allocation': self.handle_dice_allocation,
            'reconnect': self.handle_reconnect,
            'ko_switch_choice': self.handle_ko_switch_choice,
        }

        handler = handlers.get(message_type)
        if handler:
            await handler(content)
        else:
            await self.send_json({
                'type': 'error',
                'message': f'Unknown message type: {message_type}',
            })

    async def handle_battle_init(self, data):
        """Initialize battle state and send to client."""
        try:
            battle = await self.get_battle()
            if not battle:
                await self.send_json({
                    'type': 'error',
                    'message': 'Battle not found',
                })
                return

            state = await self.get_battle_state(battle)

            await self.send_json({
                'type': 'battle_state',
                **state,
            })

            # If battle is active, start the first turn
            if battle.status == 'ACTIVE' and battle.current_turn == 0:
                await self.start_turn()

        except Exception as e:
            await self.send_json({
                'type': 'error',
                'message': str(e),
            })

    async def handle_reconnect(self, data):
        """Handle reconnection - send current state."""
        battle = await self.get_battle()
        if battle:
            state = await self.get_battle_state(battle)
            await self.send_json({
                'type': 'battle_state',
                **state,
            })

            # Re-send KO switch prompt if one was pending
            if battle.rewards.get('pending_ko_switch'):
                available_cores = await self.get_alive_cores(battle)
                await self.send_json({
                    'type': 'ko_switch_prompt',
                    'available_cores': available_cores,
                })

    async def handle_player_action(self, data):
        """Process player action (move/switch/pass/gain_resource)."""
        action_type = data.get('action_type')
        action_data = data.get('action_data', {})

        battle = await self.get_battle()
        if not battle or battle.status != 'ACTIVE':
            await self.send_json({
                'type': 'error',
                'message': 'Battle not active',
            })
            return

        # Validate player action
        is_valid, error = await self.validate_action(battle, 'player', action_type, action_data)
        if not is_valid:
            await self.send_json({
                'type': 'action_rejected',
                'reason': error,
            })
            return

        # Gain resource: roll dice, send to client, wait for allocation
        if action_type == 'gain_resource':
            player_dice = await self.roll_dice(battle, 'player')

            battle = await self.get_battle()
            battle.rewards['pending_player_dice'] = player_dice
            await self.save_battle_rewards(battle)

            await self.send_json({
                'type': 'resource_dice',
                'player_dice': player_dice,
            })
            return  # Wait for dice_allocation message

        # Execute player action (move/switch/pass)
        player_result = await self.execute_action(battle, 'player', action_type, action_data)

        # Resolve NPC action and finish the turn
        await self.resolve_npc_and_finish_turn(battle, player_result)

    async def handle_dice_allocation(self, data):
        """Handle dice allocation from player.

        Turn 1 (free resource round): apply both teams' dice, send dice_allocated, start turn 2.
        Turn 2+ (gain_resource action): apply player dice, then resolve NPC action and finish turn.
        """
        allocations = data.get('allocations', [])

        battle = await self.get_battle()
        if not battle:
            return

        # Apply player allocations
        player_pools = await self.allocate_dice(battle, 'player', allocations)

        if battle.current_turn == 1:
            # Turn 1: Free resource round — also allocate NPC dice
            npc_rolls = battle.rewards.get('pending_npc_dice', [])
            npc_allocations = npc_ai.allocate_npc_dice(battle, npc_rolls)
            npc_pools = await self.allocate_dice(battle, 'npc', npc_allocations)

            # Clear pending dice
            battle = await self.get_battle()
            if 'pending_player_dice' in battle.rewards:
                del battle.rewards['pending_player_dice']
            if 'pending_npc_dice' in battle.rewards:
                del battle.rewards['pending_npc_dice']
            await self.save_battle_rewards(battle)

            # Send allocation results
            state = await self.get_battle_state(battle)
            await self.send_json({
                'type': 'dice_allocated',
                'player_pools': player_pools,
                'enemy_pools': npc_pools,
                'battle_state': state,
            })

            # Free round done — start turn 2
            await self.start_turn()
        else:
            # Turn 2+: This is the follow-up to a gain_resource action
            # Clear pending player dice
            battle = await self.get_battle()
            if 'pending_player_dice' in battle.rewards:
                del battle.rewards['pending_player_dice']
            await self.save_battle_rewards(battle)

            # Player's gain_resource result
            player_result = {
                'action_type': 'gain_resource',
                'success': True,
                'pools': player_pools,
            }

            # Resolve NPC action and finish the turn
            await self.resolve_npc_and_finish_turn(battle, player_result)

    async def resolve_npc_and_finish_turn(self, battle, player_result):
        """Get NPC action, execute it, check KOs/battle end, send results, start next turn."""
        # Get NPC action
        npc_action = await self.get_npc_action(battle)

        # Execute NPC action
        npc_result = await self.execute_action(
            battle, 'npc',
            npc_action['action_type'],
            npc_action
        )

        # Refresh battle state
        battle = await self.get_battle()

        # Check for KO'd active cores and handle mandatory switches
        waiting_for_player = await self.handle_ko_switches(battle)

        # Check for battle end
        player_defeated = await self.check_team_defeated(battle, 'player')
        npc_defeated = await self.check_team_defeated(battle, 'npc')

        if player_defeated or npc_defeated:
            winner = 'npc' if player_defeated else 'player'
            await self.end_battle(battle, winner)
            return

        # Send action results
        state = await self.get_battle_state(battle)

        await self.send_json({
            'type': 'action_result',
            'player_action': player_result,
            'enemy_action': npc_result,
            'battle_state': state,
        })

        # If waiting for player KO switch choice, don't start next turn yet
        if waiting_for_player:
            return

        # Start next turn
        await self.start_turn()

    async def start_turn(self):
        """Start a new turn. Turn 1 is a free resource round; turn 2+ is action-based."""
        battle = await self.get_battle()
        if not battle or battle.status != 'ACTIVE':
            return

        # Increment turn
        battle.current_turn += 1
        await self.save_battle(battle)

        if battle.current_turn == 1:
            # Turn 1: Free resource round — roll dice for both teams
            player_dice = await self.roll_dice(battle, 'player')
            npc_dice = await self.roll_dice(battle, 'npc')

            # Store pending dice for allocation
            battle = await self.get_battle()
            battle.rewards['pending_player_dice'] = player_dice
            battle.rewards['pending_npc_dice'] = npc_dice
            await self.save_battle_rewards(battle)

            await self.send_json({
                'type': 'turn_start',
                'turn_number': battle.current_turn,
                'is_free_resource_turn': True,
                'player_dice': player_dice,
                'enemy_dice': npc_dice,
            })
        else:
            # Turn 2+: Normal action turn — no automatic dice
            await self.send_json({
                'type': 'turn_start',
                'turn_number': battle.current_turn,
                'is_free_resource_turn': False,
            })

    async def handle_ko_switches(self, battle):
        """Handle mandatory switches when active core is KO'd.

        Returns True if waiting for player to choose a replacement core.
        """
        waiting_for_player = False

        # Check player
        player_team = await self.get_player_team(battle)
        if player_team:
            active_state = await self.get_active_core_state(player_team)
            if active_state and active_state.is_knocked_out:
                available_cores = await self.get_alive_cores(battle)
                if len(available_cores) >= 2:
                    # Multiple choices — prompt the player
                    battle = await self.get_battle()
                    battle.rewards['pending_ko_switch'] = True
                    await self.save_battle_rewards(battle)

                    await self.send_json({
                        'type': 'ko_switch_prompt',
                        'available_cores': available_cores,
                    })
                    waiting_for_player = True
                elif len(available_cores) == 1:
                    # Only one option — auto-switch
                    alive_idx = available_cores[0]['index']
                    await self.execute_action(battle, 'player', 'switch', {'new_core_index': alive_idx})
                    await self.send_json({
                        'type': 'forced_switch',
                        'team': 'player',
                        'new_core_index': alive_idx,
                    })

        # Check NPC (always auto-switch)
        battle = await self.get_battle()
        npc_team = battle.rewards.get('npc_team', {})
        active_idx = npc_team.get('active_core_index', 0)
        cores = npc_team.get('cores', [])
        if cores and active_idx < len(cores):
            if cores[active_idx].get('is_knocked_out'):
                alive_idx = npc_ai.find_alive_core(cores, exclude_idx=active_idx)
                if alive_idx is not None:
                    await self.execute_action(battle, 'npc', 'switch', {'new_core_index': alive_idx})
                    await self.send_json({
                        'type': 'forced_switch',
                        'team': 'enemy',
                        'new_core_index': alive_idx,
                    })

        return waiting_for_player

    async def handle_ko_switch_choice(self, data):
        """Handle player's choice of replacement core after a KO."""
        new_core_index = data.get('new_core_index')

        battle = await self.get_battle()
        if not battle or battle.status != 'ACTIVE':
            await self.send_json({
                'type': 'error',
                'message': 'Battle not active',
            })
            return

        if not battle.rewards.get('pending_ko_switch'):
            await self.send_json({
                'type': 'error',
                'message': 'No pending KO switch',
            })
            return

        # Validate the chosen core
        available_cores = await self.get_alive_cores(battle)
        valid_indices = [c['index'] for c in available_cores]

        if new_core_index not in valid_indices:
            await self.send_json({
                'type': 'ko_switch_prompt',
                'available_cores': available_cores,
                'error': 'Invalid core selection. Choose an alive, non-active core.',
            })
            return

        # Execute the switch
        await self.execute_action(battle, 'player', 'switch', {'new_core_index': new_core_index})

        # Clear the pending flag
        battle = await self.get_battle()
        del battle.rewards['pending_ko_switch']
        await self.save_battle_rewards(battle)

        # Send forced_switch confirmation
        await self.send_json({
            'type': 'forced_switch',
            'team': 'player',
            'new_core_index': new_core_index,
        })

        # Start next turn
        await self.start_turn()

    async def end_battle(self, battle, winner_side):
        """End the battle and send results."""
        result = await self.finalize_battle(battle, winner_side)

        # Update arena progress
        if winner_side == 'player':
            await self.update_arena_progress_win(battle)
        else:
            await self.update_arena_progress_loss(battle)

        state = await self.get_battle_state(battle)

        await self.send_json({
            'type': 'battle_end',
            'result': 'win' if winner_side == 'player' else 'lose',
            'rewards': result.get('rewards', {}),
            'battle_state': state,
        })

    # Database operations (sync_to_async wrappers)

    @database_sync_to_async
    def get_battle(self):
        try:
            return Battle.objects.get(id=self.battle_id)
        except Battle.DoesNotExist:
            return None

    @database_sync_to_async
    def get_battle_state(self, battle):
        return battle_engine.serialize_battle_state(battle)

    @database_sync_to_async
    def validate_action(self, battle, team_side, action_type, action_data):
        return battle_engine.validate_action(battle, team_side, action_type, action_data)

    @database_sync_to_async
    def execute_action(self, battle, team_side, action_type, action_data):
        if action_type == 'move':
            return battle_engine.execute_move(battle, team_side, action_data)
        elif action_type == 'switch':
            return battle_engine.execute_switch(battle, team_side, action_data.get('new_core_index', 0))
        elif action_type == 'gain_resource':
            return battle_engine.execute_gain_resource(battle, team_side)
        else:
            return {'action_type': 'pass', 'success': True}

    @database_sync_to_async
    def get_npc_action(self, battle):
        return npc_ai.choose_npc_action(battle)

    @database_sync_to_async
    def check_team_defeated(self, battle, team_side):
        return battle_engine.check_team_defeated(battle, team_side)

    @database_sync_to_async
    def roll_dice(self, battle, team_side):
        return battle_engine.roll_dice_for_team(battle, team_side)

    @database_sync_to_async
    def allocate_dice(self, battle, team_side, allocations):
        return battle_engine.allocate_dice(battle, team_side, allocations)

    @database_sync_to_async
    def finalize_battle(self, battle, winner_side):
        return battle_engine.end_battle(battle, winner_side)

    @database_sync_to_async
    def save_battle(self, battle):
        battle.save(update_fields=['current_turn', 'status'])

    @database_sync_to_async
    def save_battle_rewards(self, battle):
        battle.save(update_fields=['rewards'])

    @database_sync_to_async
    def get_player_team(self, battle):
        return battle.teams.first()

    @database_sync_to_async
    def get_active_core_state(self, team):
        return team.core_states.filter(position=team.active_core_index).first()

    @database_sync_to_async
    def find_alive_core_index(self, team):
        for state in team.core_states.filter(is_knocked_out=False):
            return state.position
        return None

    @database_sync_to_async
    def get_alive_cores(self, battle):
        """Get list of alive, non-active cores for the player team."""
        team = battle.teams.first()
        if not team:
            return []
        alive = team.core_states.filter(
            is_knocked_out=False
        ).exclude(
            position=team.active_core_index
        ).select_related('core')
        return [
            {
                'index': state.position,
                'name': state.core.name,
                'current_hp': state.current_hp,
                'max_hp': state.max_hp,
            }
            for state in alive
        ]

    @database_sync_to_async
    def update_arena_progress_win(self, battle):
        """Update arena progress for a win."""
        operator = battle.operator_1
        npc_id = battle.rewards.get('npc_id')

        if not npc_id:
            return

        try:
            npc = NPCOperator.objects.get(id=npc_id)
        except NPCOperator.DoesNotExist:
            return

        progress, _ = OperatorArenaProgress.objects.get_or_create(
            operator=operator,
            defaults={'current_rank': 'E'}
        )

        progress.arena_wins += 1
        progress.current_win_streak += 1
        progress.best_win_streak = max(progress.best_win_streak, progress.current_win_streak)

        if str(npc.id) not in progress.defeated_npcs:
            progress.defeated_npcs.append(str(npc.id))

        # Check rank unlock
        if npc.is_gate_boss and npc.unlocks_rank:
            rank_order = {'E': 0, 'D': 1, 'C': 2, 'B': 3, 'A': 4, 'S': 5}
            if rank_order.get(npc.unlocks_rank, 0) > rank_order.get(progress.current_rank, 0):
                progress.current_rank = npc.unlocks_rank

        progress.save()

        # Award bits
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

    @database_sync_to_async
    def update_arena_progress_loss(self, battle):
        """Update arena progress for a loss."""
        operator = battle.operator_1
        npc_id = battle.rewards.get('npc_id')

        if not npc_id:
            return

        try:
            npc = NPCOperator.objects.get(id=npc_id)
        except NPCOperator.DoesNotExist:
            return

        progress, _ = OperatorArenaProgress.objects.get_or_create(
            operator=operator,
            defaults={'current_rank': 'E'}
        )

        progress.arena_losses += 1
        progress.current_win_streak = 0
        progress.save()

        # Send lose mail
        Mail.objects.create(
            operator=operator,
            sender_name=npc.call_sign,
            mail_type='OPERATOR',
            subject=npc.lose_mail_subject,
            body=npc.lose_mail_body
        )
