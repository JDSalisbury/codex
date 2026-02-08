import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunks
export const fetchArenaNPCs = createAsyncThunk(
  'arena/fetchNPCs',
  async ({ rank, operatorId }, { rejectWithValue }) => {
    try {
      const data = await api.getArenaNPCs(rank, operatorId);
      return { rank, npcs: data };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchNPCDetail = createAsyncThunk(
  'arena/fetchNPCDetail',
  async ({ npcId, operatorId }, { rejectWithValue }) => {
    try {
      const data = await api.getNPCDetail(npcId, operatorId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchArenaProgress = createAsyncThunk(
  'arena/fetchProgress',
  async (operatorId, { rejectWithValue }) => {
    try {
      const data = await api.getArenaProgress(operatorId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const challengeNPC = createAsyncThunk(
  'arena/challengeNPC',
  async ({ npcId, operatorId, outcome }, { rejectWithValue }) => {
    try {
      const data = await api.challengeNPC(npcId, operatorId, outcome);
      return { npcId, outcome, ...data };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  npcs: [],
  selectedNPC: null,
  progress: null,
  currentRank: 'E',
  challengeResult: null,
  loading: false,
  detailLoading: false,
  progressLoading: false,
  challengeLoading: false,
  error: null,
};

const arenaSlice = createSlice({
  name: 'arena',
  initialState,
  reducers: {
    setCurrentRank: (state, action) => {
      state.currentRank = action.payload;
    },
    selectNPC: (state, action) => {
      state.selectedNPC = action.payload;
    },
    clearSelectedNPC: (state) => {
      state.selectedNPC = null;
    },
    clearChallengeResult: (state) => {
      state.challengeResult = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch NPCs
      .addCase(fetchArenaNPCs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchArenaNPCs.fulfilled, (state, action) => {
        state.loading = false;
        state.npcs = action.payload.npcs;
        state.currentRank = action.payload.rank;
      })
      .addCase(fetchArenaNPCs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch NPC Detail
      .addCase(fetchNPCDetail.pending, (state) => {
        state.detailLoading = true;
        state.error = null;
      })
      .addCase(fetchNPCDetail.fulfilled, (state, action) => {
        state.detailLoading = false;
        state.selectedNPC = action.payload;
      })
      .addCase(fetchNPCDetail.rejected, (state, action) => {
        state.detailLoading = false;
        state.error = action.payload;
      })
      // Fetch Progress
      .addCase(fetchArenaProgress.pending, (state) => {
        state.progressLoading = true;
      })
      .addCase(fetchArenaProgress.fulfilled, (state, action) => {
        state.progressLoading = false;
        state.progress = action.payload;
      })
      .addCase(fetchArenaProgress.rejected, (state, action) => {
        state.progressLoading = false;
        state.error = action.payload;
      })
      // Challenge NPC
      .addCase(challengeNPC.pending, (state) => {
        state.challengeLoading = true;
        state.challengeResult = null;
      })
      .addCase(challengeNPC.fulfilled, (state, action) => {
        state.challengeLoading = false;
        state.challengeResult = action.payload;
        state.progress = action.payload.progress;
        // Update NPC defeated status in list
        const npcIndex = state.npcs.findIndex(n => n.id === action.payload.npcId);
        if (npcIndex !== -1 && action.payload.outcome === 'win') {
          state.npcs[npcIndex].is_defeated = true;
        }
        // Update selected NPC if same
        if (state.selectedNPC && state.selectedNPC.id === action.payload.npcId && action.payload.outcome === 'win') {
          state.selectedNPC.is_defeated = true;
        }
      })
      .addCase(challengeNPC.rejected, (state, action) => {
        state.challengeLoading = false;
        state.error = action.payload;
      });
  },
});

export const {
  setCurrentRank,
  selectNPC,
  clearSelectedNPC,
  clearChallengeResult,
  clearError,
} = arenaSlice.actions;

// Selectors
export const selectArenaNPCs = (state) => state.arena.npcs;
export const selectSelectedNPC = (state) => state.arena.selectedNPC;
export const selectArenaProgress = (state) => state.arena.progress;
export const selectCurrentRank = (state) => state.arena.currentRank;
export const selectChallengeResult = (state) => state.arena.challengeResult;
export const selectArenaLoading = (state) => state.arena.loading;
export const selectArenaDetailLoading = (state) => state.arena.detailLoading;
export const selectArenaProgressLoading = (state) => state.arena.progressLoading;
export const selectChallengeLoading = (state) => state.arena.challengeLoading;
export const selectArenaError = (state) => state.arena.error;

// Derived selectors
export const selectIsRankUnlocked = (state, rank) => {
  const progress = state.arena.progress;
  if (!progress) return rank === 'E';
  const rankOrder = { 'E': 0, 'D': 1, 'C': 2, 'B': 3, 'A': 4, 'S': 5 };
  return rankOrder[rank] <= rankOrder[progress.current_rank];
};

export default arenaSlice.reducer;
