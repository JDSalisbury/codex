import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunks
export const fetchMoves = createAsyncThunk(
  'moves/fetchMoves',
  async (params = {}, { rejectWithValue }) => {
    try {
      const data = await api.getMoves(params);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchMove = createAsyncThunk(
  'moves/fetchMove',
  async (moveId, { rejectWithValue }) => {
    try {
      const data = await api.getMove(moveId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchMoveShop = createAsyncThunk(
  'moves/fetchMoveShop',
  async (_, { rejectWithValue }) => {
    try {
      const data = await api.getMoveShop();
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const purchaseMove = createAsyncThunk(
  'moves/purchaseMove',
  async ({ coreId, moveId }, { rejectWithValue }) => {
    try {
      const data = await api.purchaseMove(coreId, moveId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  items: [],
  selectedMove: null,
  filters: {
    type: null,
    damageType: null,
    rarity: null,
  },
  loading: false,
  error: null,
};

const movesSlice = createSlice({
  name: 'moves',
  initialState,
  reducers: {
    clearMoves: (state) => {
      state.items = [];
      state.selectedMove = null;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    selectMove: (state, action) => {
      state.selectedMove = action.payload;
    },
    clearSelectedMove: (state) => {
      state.selectedMove = null;
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {
        type: null,
        damageType: null,
        rarity: null,
      };
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch moves
      .addCase(fetchMoves.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMoves.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchMoves.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch single move
      .addCase(fetchMove.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMove.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedMove = action.payload;
        const index = state.items.findIndex(move => move.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        } else {
          state.items.push(action.payload);
        }
      })
      .addCase(fetchMove.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch move shop
      .addCase(fetchMoveShop.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMoveShop.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchMoveShop.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Purchase move
      .addCase(purchaseMove.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(purchaseMove.fulfilled, (state, action) => {
        state.loading = false;
        // Optionally remove purchased move from shop list
        // or mark it as owned (depends on game design)
      })
      .addCase(purchaseMove.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const {
  clearMoves,
  clearError,
  selectMove,
  clearSelectedMove,
  setFilters,
  clearFilters,
} = movesSlice.actions;

// Selectors
export const selectAllMoves = (state) => state.moves.items;
export const selectSelectedMove = (state) => state.moves.selectedMove;
export const selectMovesLoading = (state) => state.moves.loading;
export const selectMovesError = (state) => state.moves.error;
export const selectMovesFilters = (state) => state.moves.filters;
export const selectFilteredMoves = (state) => {
  const { items, filters } = state.moves;
  return items.filter(move => {
    if (filters.type && move.type !== filters.type) return false;
    if (filters.damageType && move.damage_type !== filters.damageType) return false;
    if (filters.rarity && move.rarity !== filters.rarity) return false;
    return true;
  });
};

export default movesSlice.reducer;
