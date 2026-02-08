import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "../../services/api";

// Async thunks
export const fetchCores = createAsyncThunk(
  "cores/fetchCores",
  async (garageId, { rejectWithValue }) => {
    try {
      const data = await api.getCores(garageId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchCore = createAsyncThunk(
  "cores/fetchCore",
  async (coreId, { rejectWithValue }) => {
    try {
      const data = await api.getCore(coreId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const generateCore = createAsyncThunk(
  "cores/generateCore",
  async (coreData, { rejectWithValue }) => {
    try {
      const data = await api.generateCore(coreData);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateCore = createAsyncThunk(
  "cores/updateCore",
  async ({ coreId, updates }, { rejectWithValue }) => {
    try {
      const data = await api.updateCore(coreId, updates);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const decommissionCore = createAsyncThunk(
  "cores/decommissionCore",
  async (coreId, { rejectWithValue }) => {
    try {
      const data = await api.decommissionCore(coreId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchCoreBattleInfo = createAsyncThunk(
  "cores/fetchCoreBattleInfo",
  async (coreId, { rejectWithValue }) => {
    try {
      const data = await api.getCoreBattleInfo(coreId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchCoreUpgradeInfo = createAsyncThunk(
  "cores/fetchCoreUpgradeInfo",
  async (coreId, { rejectWithValue }) => {
    try {
      const data = await api.getCoreUpgradeInfo(coreId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchCoreEquippedMoves = createAsyncThunk(
  "cores/fetchCoreEquippedMoves",
  async (coreId, { rejectWithValue }) => {
    try {
      const data = await api.getCoreEquippedMoves(coreId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchCoreAvailableMoves = createAsyncThunk(
  "cores/fetchCoreAvailableMoves",
  async (coreId, { rejectWithValue }) => {
    try {
      const data = await api.getCoreAvailableMoves(coreId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const equipMove = createAsyncThunk(
  "cores/equipMove",
  async ({ coreId, moveId, slot }, { rejectWithValue }) => {
    try {
      const data = await api.equipMove(coreId, moveId, slot);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const unequipMove = createAsyncThunk(
  "cores/unequipMove",
  async ({ coreId, slot }, { rejectWithValue }) => {
    try {
      const data = await api.unequipMove(coreId, slot);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  items: [],
  selectedCore: null,
  coreBattleInfo: {},
  coreUpgradeInfo: {},
  equippedMoves: {},
  availableMoves: {},
  loading: false,
  error: null,
};

const coresSlice = createSlice({
  name: "cores",
  initialState,
  reducers: {
    clearCores: (state) => {
      state.items = [];
      state.selectedCore = null;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    selectCore: (state, action) => {
      state.selectedCore = action.payload;
    },
    clearSelectedCore: (state) => {
      state.selectedCore = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch cores
      .addCase(fetchCores.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCores.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchCores.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch single core
      .addCase(fetchCore.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCore.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedCore = action.payload;
        const index = state.items.findIndex(
          (core) => core.id === action.payload.id
        );
        if (index !== -1) {
          state.items[index] = action.payload;
        } else {
          state.items.push(action.payload);
        }
      })
      .addCase(fetchCore.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.coreBattleInfo[action.meta.arg] =
          action.payload.battle_info || null;
      })
      // Generate core
      .addCase(generateCore.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(generateCore.fulfilled, (state, action) => {
        state.loading = false;
        state.items.push(action.payload);
      })
      .addCase(generateCore.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update core
      .addCase(updateCore.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateCore.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.items.findIndex(
          (core) => core.id === action.payload.id
        );
        if (index !== -1) {
          state.items[index] = action.payload;
        }
        if (state.selectedCore?.id === action.payload.id) {
          state.selectedCore = action.payload;
        }
      })
      .addCase(updateCore.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Decommission core
      .addCase(decommissionCore.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(decommissionCore.fulfilled, (state, action) => {
        state.loading = false;
        state.items = state.items.filter(
          (core) => core.id !== action.payload.id
        );
        if (state.selectedCore?.id === action.payload.id) {
          state.selectedCore = null;
        }
      })
      .addCase(decommissionCore.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch core battle info
      .addCase(fetchCoreBattleInfo.fulfilled, (state, action) => {
        state.coreBattleInfo[action.meta.arg] = action.payload;
      })
      // Fetch core upgrade info
      .addCase(fetchCoreUpgradeInfo.fulfilled, (state, action) => {
        state.coreUpgradeInfo[action.meta.arg] = action.payload;
      })
      // Fetch equipped moves
      .addCase(fetchCoreEquippedMoves.fulfilled, (state, action) => {
        state.equippedMoves[action.meta.arg] = action.payload;
      })
      // Fetch available moves
      .addCase(fetchCoreAvailableMoves.fulfilled, (state, action) => {
        state.availableMoves[action.meta.arg] = action.payload;
      })
      // Equip move
      .addCase(equipMove.fulfilled, (state, action) => {
        const coreId = action.meta.arg.coreId;
        if (!state.equippedMoves[coreId]) {
          state.equippedMoves[coreId] = [];
        }
        const index = state.equippedMoves[coreId].findIndex(
          (em) => em.slot === action.payload.slot
        );
        if (index !== -1) {
          state.equippedMoves[coreId][index] = action.payload;
        } else {
          state.equippedMoves[coreId].push(action.payload);
        }
      })
      // Unequip move
      .addCase(unequipMove.fulfilled, (state, action) => {
        const coreId = action.meta.arg.coreId;
        const slot = action.meta.arg.slot;
        if (state.equippedMoves[coreId]) {
          state.equippedMoves[coreId] = state.equippedMoves[coreId].filter(
            (em) => em.slot !== slot
          );
        }
      });
  },
});

export const { clearCores, clearError, selectCore, clearSelectedCore } =
  coresSlice.actions;

// Selectors
export const selectAllCores = (state) => state.cores.items;
export const selectSelectedCore = (state) => state.cores.selectedCore;
export const selectCoresLoading = (state) => state.cores.loading;
export const selectCoresError = (state) => state.cores.error;
export const selectCoreBattleInfo = (coreId) => (state) =>
  state.cores.coreBattleInfo[coreId];
export const selectCoreUpgradeInfo = (coreId) => (state) =>
  state.cores.coreUpgradeInfo[coreId];
export const selectCoreEquippedMoves = (coreId) => (state) =>
  state.cores.equippedMoves[coreId] || [];
export const selectCoreAvailableMoves = (coreId) => (state) =>
  state.cores.availableMoves[coreId] || [];

export default coresSlice.reducer;
