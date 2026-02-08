import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunks
export const fetchMail = createAsyncThunk(
  'mail/fetchMail',
  async (operatorId, { rejectWithValue }) => {
    try {
      const data = await api.getMail(operatorId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchMailDetail = createAsyncThunk(
  'mail/fetchMailDetail',
  async (mailId, { rejectWithValue }) => {
    try {
      const data = await api.getMailDetail(mailId);
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const markMailRead = createAsyncThunk(
  'mail/markMailRead',
  async (mailId, { rejectWithValue }) => {
    try {
      await api.markMailRead(mailId);
      return mailId;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchUnreadCount = createAsyncThunk(
  'mail/fetchUnreadCount',
  async (operatorId, { rejectWithValue }) => {
    try {
      const data = await api.getUnreadCount(operatorId);
      return data.unread_count;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  items: [],
  selectedMail: null,
  filters: {
    sender: null,
    mailType: null,
  },
  unreadCount: 0,
  loading: false,
  detailLoading: false,
  error: null,
};

const mailSlice = createSlice({
  name: 'mail',
  initialState,
  reducers: {
    selectMail: (state, action) => {
      state.selectedMail = action.payload;
    },
    clearSelectedMail: (state) => {
      state.selectedMail = null;
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = { sender: null, mailType: null };
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch mail list
      .addCase(fetchMail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMail.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchMail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch mail detail
      .addCase(fetchMailDetail.pending, (state) => {
        state.detailLoading = true;
        state.error = null;
      })
      .addCase(fetchMailDetail.fulfilled, (state, action) => {
        state.detailLoading = false;
        state.selectedMail = action.payload;
        // Update the item in the list if it exists
        const index = state.items.findIndex(m => m.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = { ...state.items[index], ...action.payload };
        }
      })
      .addCase(fetchMailDetail.rejected, (state, action) => {
        state.detailLoading = false;
        state.error = action.payload;
      })
      // Mark mail as read
      .addCase(markMailRead.fulfilled, (state, action) => {
        const mailId = action.payload;
        // Update item in list
        const index = state.items.findIndex(m => m.id === mailId);
        if (index !== -1) {
          state.items[index].is_read = true;
        }
        // Update selected mail if it's the same
        if (state.selectedMail && state.selectedMail.id === mailId) {
          state.selectedMail.is_read = true;
        }
        // Decrement unread count
        if (state.unreadCount > 0) {
          state.unreadCount -= 1;
        }
      })
      // Fetch unread count
      .addCase(fetchUnreadCount.fulfilled, (state, action) => {
        state.unreadCount = action.payload;
      });
  },
});

export const {
  selectMail,
  clearSelectedMail,
  setFilters,
  clearFilters,
  clearError,
} = mailSlice.actions;

// Selectors
export const selectAllMail = (state) => state.mail.items;
export const selectSelectedMail = (state) => state.mail.selectedMail;
export const selectMailFilters = (state) => state.mail.filters;
export const selectUnreadCount = (state) => state.mail.unreadCount;
export const selectMailLoading = (state) => state.mail.loading;
export const selectMailDetailLoading = (state) => state.mail.detailLoading;
export const selectMailError = (state) => state.mail.error;

// Filtered mail selector
export const selectFilteredMail = (state) => {
  const { items, filters } = state.mail;
  let filtered = [...items];

  if (filters.sender) {
    filtered = filtered.filter(m => m.sender_name === filters.sender);
  }
  if (filters.mailType) {
    filtered = filtered.filter(m => m.mail_type === filters.mailType);
  }

  return filtered;
};

// Unique senders selector
export const selectUniqueSenders = (state) => {
  const senders = state.mail.items.map(m => m.sender_name);
  return [...new Set(senders)].sort();
};

export default mailSlice.reducer;
