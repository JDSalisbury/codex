// frontend/src/store/slices/battleSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunk to start a battle
export const startBattle = createAsyncThunk(
  'battle/startBattle',
  async ({ npcId, operatorId }, { rejectWithValue }) => {
    try {
      const response = await api.startBattle(npcId, operatorId);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  battleId: null,
  status: 'idle', // idle | connecting | active | ended
  phase: 'waiting', // waiting | dice_roll | action_select | resolution

  playerTeam: null,
  enemyTeam: null,

  currentTurn: 0,
  pendingDiceRolls: [],
  turnLog: [],

  result: null, // win | lose
  rewards: null,

  selectedMove: null,
  connected: false,

  // Loading states
  loading: false,
  error: null,

  // Last action results
  lastPlayerAction: null,
  lastEnemyAction: null,

  // NPC info
  npcId: null,
  npcName: null,
};

const battleSlice = createSlice({
  name: 'battle',
  initialState,
  reducers: {
    // WebSocket connection state
    setConnected: (state, action) => {
      state.connected = action.payload;
      if (action.payload) {
        state.status = 'active';
      }
    },

    // Set battle ID when starting
    setBattleId: (state, action) => {
      state.battleId = action.payload;
      state.status = 'connecting';
    },

    // Update full battle state from server
    setBattleState: (state, action) => {
      const data = action.payload;
      state.playerTeam = data.player_team;
      state.enemyTeam = data.enemy_team;
      state.currentTurn = data.current_turn;
      state.npcId = data.npc_id;
      state.npcName = data.npc_name;

      if (data.status === 'COMPLETED') {
        state.status = 'ended';
      }
    },

    // Turn start - dice phase
    setTurnStart: (state, action) => {
      const { turn_number, player_dice, enemy_dice } = action.payload;
      state.currentTurn = turn_number;
      state.pendingDiceRolls = player_dice;
      state.phase = 'dice_roll';

      // Add to turn log
      state.turnLog.push({
        type: 'turn_start',
        turn: turn_number,
        timestamp: new Date().toISOString(),
      });
    },

    // Dice allocated - move to action selection
    setDiceAllocated: (state, action) => {
      const { player_pools, enemy_pools, battle_state } = action.payload;
      state.pendingDiceRolls = [];
      state.phase = 'action_select';

      // Update pools from battle_state
      if (battle_state) {
        state.playerTeam = battle_state.player_team;
        state.enemyTeam = battle_state.enemy_team;
      }
    },

    // Move selected by player
    setSelectedMove: (state, action) => {
      state.selectedMove = action.payload;
    },

    // Action result received
    setActionResult: (state, action) => {
      const { player_action, enemy_action, battle_state } = action.payload;
      state.lastPlayerAction = player_action;
      state.lastEnemyAction = enemy_action;
      state.phase = 'resolution';

      // Update battle state
      if (battle_state) {
        state.playerTeam = battle_state.player_team;
        state.enemyTeam = battle_state.enemy_team;
      }

      // Add to turn log
      state.turnLog.push({
        type: 'action',
        turn: state.currentTurn,
        player: player_action,
        enemy: enemy_action,
        timestamp: new Date().toISOString(),
      });

      // Clear selection
      state.selectedMove = null;
    },

    // Action rejected
    setActionRejected: (state, action) => {
      state.error = action.payload.reason;
      state.selectedMove = null;
    },

    // Forced switch (KO)
    setForcedSwitch: (state, action) => {
      const { team, new_core_index } = action.payload;

      if (team === 'player' && state.playerTeam) {
        state.playerTeam.active_core_index = new_core_index;
      } else if (team === 'enemy' && state.enemyTeam) {
        state.enemyTeam.active_core_index = new_core_index;
      }

      state.turnLog.push({
        type: 'forced_switch',
        team,
        new_index: new_core_index,
        timestamp: new Date().toISOString(),
      });
    },

    // Battle ended
    setBattleEnd: (state, action) => {
      const { result, rewards, battle_state } = action.payload;
      state.result = result;
      state.rewards = rewards;
      state.status = 'ended';
      state.phase = 'waiting';

      if (battle_state) {
        state.playerTeam = battle_state.player_team;
        state.enemyTeam = battle_state.enemy_team;
      }

      state.turnLog.push({
        type: 'battle_end',
        result,
        rewards,
        timestamp: new Date().toISOString(),
      });
    },

    // Error handling
    setError: (state, action) => {
      state.error = action.payload;
    },

    clearError: (state) => {
      state.error = null;
    },

    // Reset battle state
    resetBattle: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      .addCase(startBattle.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(startBattle.fulfilled, (state, action) => {
        state.loading = false;
        state.battleId = action.payload.battle_id;
        state.status = 'connecting';
      })
      .addCase(startBattle.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const {
  setConnected,
  setBattleId,
  setBattleState,
  setTurnStart,
  setDiceAllocated,
  setSelectedMove,
  setActionResult,
  setActionRejected,
  setForcedSwitch,
  setBattleEnd,
  setError,
  clearError,
  resetBattle,
} = battleSlice.actions;

// Selectors
export const selectBattleId = (state) => state.battle.battleId;
export const selectBattleStatus = (state) => state.battle.status;
export const selectBattlePhase = (state) => state.battle.phase;
export const selectPlayerTeam = (state) => state.battle.playerTeam;
export const selectEnemyTeam = (state) => state.battle.enemyTeam;
export const selectCurrentTurn = (state) => state.battle.currentTurn;
export const selectPendingDiceRolls = (state) => state.battle.pendingDiceRolls;
export const selectTurnLog = (state) => state.battle.turnLog;
export const selectBattleResult = (state) => state.battle.result;
export const selectBattleRewards = (state) => state.battle.rewards;
export const selectSelectedMove = (state) => state.battle.selectedMove;
export const selectConnected = (state) => state.battle.connected;
export const selectBattleLoading = (state) => state.battle.loading;
export const selectBattleError = (state) => state.battle.error;
export const selectLastPlayerAction = (state) => state.battle.lastPlayerAction;
export const selectLastEnemyAction = (state) => state.battle.lastEnemyAction;
export const selectNpcName = (state) => state.battle.npcName;

// Computed selectors
export const selectActivePlayerCore = (state) => {
  const team = state.battle.playerTeam;
  if (!team || !team.cores) return null;
  return team.cores[team.active_core_index] || null;
};

export const selectActiveEnemyCore = (state) => {
  const team = state.battle.enemyTeam;
  if (!team || !team.cores) return null;
  return team.cores[team.active_core_index] || null;
};

export default battleSlice.reducer;
