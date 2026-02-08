import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunks
export const fetchOperator = createAsyncThunk(
  'operator/fetchOperator',
  async (operatorId, { rejectWithValue }) => {
    try {
      const data = await api.getOperator(operatorId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const createOperator = createAsyncThunk(
  'operator/createOperator',
  async (operatorData, { rejectWithValue }) => {
    try {
      const data = await api.createOperator(operatorData);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateOperator = createAsyncThunk(
  'operator/updateOperator',
  async ({ operatorId, updates }, { rejectWithValue }) => {
    try {
      const data = await api.updateOperator(operatorId, updates);
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

const operatorSlice = createSlice({
  name: 'operator',
  initialState,
  reducers: {
    clearOperator: (state) => {
      state.current = null;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch operator
      .addCase(fetchOperator.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOperator.fulfilled, (state, action) => {
        state.loading = false;
        state.current = action.payload;
      })
      .addCase(fetchOperator.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Create operator
      .addCase(createOperator.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createOperator.fulfilled, (state, action) => {
        state.loading = false;
        state.current = action.payload;
      })
      .addCase(createOperator.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update operator
      .addCase(updateOperator.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateOperator.fulfilled, (state, action) => {
        state.loading = false;
        state.current = action.payload;
      })
      .addCase(updateOperator.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearOperator, clearError } = operatorSlice.actions;

// Selectors
export const selectOperator = (state) => state.operator.current;
export const selectOperatorLoading = (state) => state.operator.loading;
export const selectOperatorError = (state) => state.operator.error;

export default operatorSlice.reducer;
