import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunks
export const fetchScrapyard = createAsyncThunk(
  'scrapyard/fetchScrapyard',
  async (_, { rejectWithValue }) => {
    try {
      const data = await api.getScrapyard();
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchDecommissionedCores = createAsyncThunk(
  'scrapyard/fetchDecommissionedCores',
  async (_, { rejectWithValue }) => {
    try {
      const data = await api.getDecommissionedCores();
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const recommissionCore = createAsyncThunk(
  'scrapyard/recommissionCore',
  async (coreId, { rejectWithValue }) => {
    try {
      const data = await api.recommissionCore(coreId);
      return { coreId, data };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  scrapyard: null,
  decommissionedCores: [],
  loading: false,
  error: null,
};

const scrapyardSlice = createSlice({
  name: 'scrapyard',
  initialState,
  reducers: {
    clearScrapyard: (state) => {
      state.scrapyard = null;
      state.decommissionedCores = [];
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch scrapyard
      .addCase(fetchScrapyard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchScrapyard.fulfilled, (state, action) => {
        state.loading = false;
        state.scrapyard = action.payload;
      })
      .addCase(fetchScrapyard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch decommissioned cores
      .addCase(fetchDecommissionedCores.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDecommissionedCores.fulfilled, (state, action) => {
        state.loading = false;
        state.decommissionedCores = action.payload;
      })
      .addCase(fetchDecommissionedCores.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Recommission core
      .addCase(recommissionCore.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(recommissionCore.fulfilled, (state, action) => {
        state.loading = false;
        state.decommissionedCores = state.decommissionedCores.filter(
          core => core.id !== action.payload.coreId
        );
      })
      .addCase(recommissionCore.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearScrapyard, clearError } = scrapyardSlice.actions;

// Selectors
export const selectScrapyard = (state) => state.scrapyard.scrapyard;
export const selectDecommissionedCores = (state) => state.scrapyard.decommissionedCores;
export const selectScrapyardLoading = (state) => state.scrapyard.loading;
export const selectScrapyardError = (state) => state.scrapyard.error;

export default scrapyardSlice.reducer;
