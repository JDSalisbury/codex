import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunks
export const fetchGarage = createAsyncThunk(
  'garage/fetchGarage',
  async (garageId, { rejectWithValue }) => {
    try {
      const data = await api.getGarage(garageId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchGarageByOperator = createAsyncThunk(
  'garage/fetchGarageByOperator',
  async (operatorId, { rejectWithValue }) => {
    try {
      const data = await api.getGarageByOperator(operatorId);
      // API returns an array, extract the first garage
      return Array.isArray(data) && data.length > 0 ? data[0] : null;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateGarage = createAsyncThunk(
  'garage/updateGarage',
  async ({ garageId, updates }, { rejectWithValue }) => {
    try {
      const data = await api.updateGarage(garageId, updates);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  current: null,
  loading: false,
  error: null,
};

const garageSlice = createSlice({
  name: 'garage',
  initialState,
  reducers: {
    clearGarage: (state) => {
      state.current = null;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateLoadout: (state, action) => {
      if (state.current) {
        state.current.loadouts = action.payload;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch garage
      .addCase(fetchGarage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchGarage.fulfilled, (state, action) => {
        state.loading = false;
        state.current = action.payload;
      })
      .addCase(fetchGarage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch garage by operator
      .addCase(fetchGarageByOperator.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchGarageByOperator.fulfilled, (state, action) => {
        state.loading = false;
        state.current = action.payload;
      })
      .addCase(fetchGarageByOperator.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update garage
      .addCase(updateGarage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateGarage.fulfilled, (state, action) => {
        state.loading = false;
        state.current = action.payload;
      })
      .addCase(updateGarage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearGarage, clearError, updateLoadout } = garageSlice.actions;

// Selectors
export const selectGarage = (state) => state.garage.current;
export const selectGarageLoading = (state) => state.garage.loading;
export const selectGarageError = (state) => state.garage.error;
export const selectGarageCapacity = (state) => {
  if (!state.garage.current) return { used: 0, total: 0, available: 0 };
  const used = state.garage.current.active_cores_count || 0;
  const total = state.garage.current.bay_doors || 0;
  return {
    used,
    total,
    available: total - used,
  };
};

export default garageSlice.reducer;
