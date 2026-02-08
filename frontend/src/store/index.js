import { configureStore } from '@reduxjs/toolkit';
import operatorReducer from './slices/operatorSlice';
import garageReducer from './slices/garageSlice';
import coresReducer from './slices/coresSlice';
import movesReducer from './slices/movesSlice';
import scrapyardReducer from './slices/scrapyardSlice';
import mailReducer from './slices/mailSlice';
import arenaReducer from './slices/arenaSlice';
import battleReducer from './slices/battleSlice';

export const store = configureStore({
  reducer: {
    operator: operatorReducer,
    garage: garageReducer,
    cores: coresReducer,
    moves: movesReducer,
    scrapyard: scrapyardReducer,
    mail: mailReducer,
    arena: arenaReducer,
    battle: battleReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types if needed for non-serializable values
        ignoredActions: ['your/action/type'],
      },
    }),
});

export default store;
