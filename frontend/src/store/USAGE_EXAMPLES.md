# Redux Usage Examples

This file provides examples of how to use the Redux store in your React components.

## Basic Hook Usage

```javascript
import { useSelector, useDispatch } from 'react-redux';
import { fetchOperator, selectOperator } from '../store/slices/operatorSlice';

function MyComponent() {
  const dispatch = useDispatch();
  const operator = useSelector(selectOperator);

  // Fetch operator on mount
  useEffect(() => {
    dispatch(fetchOperator('operator-id-here'));
  }, [dispatch]);

  return <div>{operator?.name}</div>;
}
```

## Operator Operations

```javascript
import { useSelector, useDispatch } from 'react-redux';
import {
  fetchOperator,
  updateOperator,
  selectOperator,
  selectOperatorLoading,
  selectOperatorError
} from '../store/slices/operatorSlice';

function OperatorProfile() {
  const dispatch = useDispatch();
  const operator = useSelector(selectOperator);
  const loading = useSelector(selectOperatorLoading);
  const error = useSelector(selectOperatorError);

  // Fetch operator data
  useEffect(() => {
    dispatch(fetchOperator('your-operator-id'));
  }, [dispatch]);

  // Update operator data
  const handleUpdate = async () => {
    await dispatch(updateOperator({
      operatorId: operator.id,
      updates: { level: operator.level + 1 }
    }));
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>{operator?.name}</h1>
      <p>Level: {operator?.level}</p>
      <p>Wins: {operator?.wins} | Losses: {operator?.losses}</p>
      <p>Bits: {operator?.bits} | Premium: {operator?.premium_currency}</p>
    </div>
  );
}
```

## Garage and Cores

```javascript
import { useSelector, useDispatch } from 'react-redux';
import {
  fetchCores,
  selectAllCores,
  selectCoresLoading,
  generateCore
} from '../store/slices/coresSlice';
import {
  fetchGarageByOperator,
  selectGarage,
  selectGarageCapacity
} from '../store/slices/garageSlice';

function GarageView() {
  const dispatch = useDispatch();
  const cores = useSelector(selectAllCores);
  const garage = useSelector(selectGarage);
  const capacity = useSelector(selectGarageCapacity);
  const loading = useSelector(selectCoresLoading);

  useEffect(() => {
    const operatorId = 'your-operator-id';
    dispatch(fetchGarageByOperator(operatorId)).then((result) => {
      if (result.payload?.id) {
        dispatch(fetchCores(result.payload.id));
      }
    });
  }, [dispatch]);

  const handleGenerateCore = async () => {
    await dispatch(generateCore({
      garage_id: garage.id,
      rarity: 'Common',
      // Add other generation parameters
    }));
  };

  return (
    <div>
      <h2>Garage</h2>
      <p>Capacity: {capacity.used} / {capacity.total}</p>
      <button
        onClick={handleGenerateCore}
        disabled={capacity.used >= capacity.total}
      >
        Generate New Core
      </button>

      <h3>Cores</h3>
      {loading ? (
        <div>Loading cores...</div>
      ) : (
        <ul>
          {cores.map(core => (
            <li key={core.id}>
              {core.name} - {core.rarity}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

## Core Details with Battle Info

```javascript
import { useSelector, useDispatch } from 'react-redux';
import {
  fetchCore,
  fetchCoreBattleInfo,
  fetchCoreEquippedMoves,
  selectSelectedCore,
  selectCoreBattleInfo,
  selectCoreEquippedMoves
} from '../store/slices/coresSlice';

function CoreDetails({ coreId }) {
  const dispatch = useDispatch();
  const core = useSelector(selectSelectedCore);
  const battleInfo = useSelector(selectCoreBattleInfo(coreId));
  const equippedMoves = useSelector(selectCoreEquippedMoves(coreId));

  useEffect(() => {
    dispatch(fetchCore(coreId));
    dispatch(fetchCoreBattleInfo(coreId));
    dispatch(fetchCoreEquippedMoves(coreId));
  }, [dispatch, coreId]);

  return (
    <div>
      <h2>{core?.name}</h2>
      <div>
        <h3>Battle Stats</h3>
        <p>HP: {battleInfo?.hp_current} / {battleInfo?.hp_max}</p>
        <p>Physical: {battleInfo?.physical_attack}</p>
        <p>Energy: {battleInfo?.energy_attack}</p>
        <p>Defense: {battleInfo?.defense}</p>
        <p>Shield: {battleInfo?.shield}</p>
        <p>Speed: {battleInfo?.speed}</p>
      </div>

      <div>
        <h3>Equipped Moves</h3>
        {equippedMoves?.map(em => (
          <div key={em.slot}>
            Slot {em.slot}: {em.move.name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Moves Library

```javascript
import { useSelector, useDispatch } from 'react-redux';
import {
  fetchMoves,
  selectFilteredMoves,
  selectMovesLoading,
  setFilters
} from '../store/slices/movesSlice';

function MovesLibrary() {
  const dispatch = useDispatch();
  const moves = useSelector(selectFilteredMoves);
  const loading = useSelector(selectMovesLoading);

  useEffect(() => {
    dispatch(fetchMoves());
  }, [dispatch]);

  const handleFilterChange = (filterType, value) => {
    dispatch(setFilters({ [filterType]: value }));
  };

  return (
    <div>
      <h2>Moves Library</h2>

      <div>
        <label>Type:</label>
        <select onChange={(e) => handleFilterChange('type', e.target.value)}>
          <option value="">All</option>
          <option value="Attack">Attack</option>
          <option value="Defense">Defense</option>
          <option value="Support">Support</option>
        </select>

        <label>Damage Type:</label>
        <select onChange={(e) => handleFilterChange('damageType', e.target.value)}>
          <option value="">All</option>
          <option value="Physical">Physical</option>
          <option value="Energy">Energy</option>
        </select>
      </div>

      {loading ? (
        <div>Loading moves...</div>
      ) : (
        <ul>
          {moves.map(move => (
            <li key={move.id}>
              {move.name} - {move.type} ({move.damage_type})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

## Equipping Moves

```javascript
import { useDispatch } from 'react-redux';
import { equipMove, unequipMove } from '../store/slices/coresSlice';

function MoveEquipButton({ coreId, moveId, slot, isEquipped }) {
  const dispatch = useDispatch();

  const handleEquip = async () => {
    try {
      await dispatch(equipMove({ coreId, moveId, slot })).unwrap();
      console.log('Move equipped successfully');
    } catch (error) {
      console.error('Failed to equip move:', error);
    }
  };

  const handleUnequip = async () => {
    try {
      await dispatch(unequipMove({ coreId, slot })).unwrap();
      console.log('Move unequipped successfully');
    } catch (error) {
      console.error('Failed to unequip move:', error);
    }
  };

  return (
    <button onClick={isEquipped ? handleUnequip : handleEquip}>
      {isEquipped ? 'Unequip' : 'Equip'}
    </button>
  );
}
```

## Scrapyard Operations

```javascript
import { useSelector, useDispatch } from 'react-redux';
import {
  fetchDecommissionedCores,
  recommissionCore,
  selectDecommissionedCores,
  selectScrapyardLoading
} from '../store/slices/scrapyardSlice';
import { decommissionCore } from '../store/slices/coresSlice';

function ScrapyardView() {
  const dispatch = useDispatch();
  const decommissioned = useSelector(selectDecommissionedCores);
  const loading = useSelector(selectScrapyardLoading);

  useEffect(() => {
    dispatch(fetchDecommissionedCores());
  }, [dispatch]);

  const handleDecommission = async (coreId) => {
    try {
      await dispatch(decommissionCore(coreId)).unwrap();
      dispatch(fetchDecommissionedCores());
      console.log('Core decommissioned');
    } catch (error) {
      console.error('Failed to decommission:', error);
    }
  };

  const handleRecommission = async (snapshotId) => {
    try {
      await dispatch(recommissionCore(snapshotId)).unwrap();
      console.log('Core recommissioned');
    } catch (error) {
      console.error('Failed to recommission:', error);
    }
  };

  return (
    <div>
      <h2>Scrapyard</h2>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <ul>
          {decommissioned.map(snapshot => (
            <li key={snapshot.id}>
              {snapshot.name} - Decommissioned on {snapshot.decommed_at}
              <button onClick={() => handleRecommission(snapshot.id)}>
                Recommission
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

## Error Handling Pattern

```javascript
import { useSelector, useDispatch } from 'react-redux';
import { useEffect } from 'react';
import {
  fetchOperator,
  selectOperator,
  selectOperatorError,
  clearError
} from '../store/slices/operatorSlice';

function ComponentWithErrorHandling() {
  const dispatch = useDispatch();
  const operator = useSelector(selectOperator);
  const error = useSelector(selectOperatorError);

  useEffect(() => {
    dispatch(fetchOperator('operator-id'));
  }, [dispatch]);

  // Clear error when component unmounts
  useEffect(() => {
    return () => {
      if (error) {
        dispatch(clearError());
      }
    };
  }, [dispatch, error]);

  if (error) {
    return (
      <div className="error">
        <p>Error: {error}</p>
        <button onClick={() => dispatch(clearError())}>Dismiss</button>
      </div>
    );
  }

  return <div>{/* Your component content */}</div>;
}
```

## Environment Configuration

Create a `.env` file in the frontend directory:

```
REACT_APP_API_URL=http://localhost:8000/api
```

This allows you to change the backend URL without modifying code.
