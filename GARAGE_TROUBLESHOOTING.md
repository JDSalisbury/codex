# Garage Frontend Troubleshooting

## Issues Fixed

### 1. Missing Core API Endpoint
**Problem:** Core viewset wasn't registered in URLs
**Fixed:** Added `CoreView` to `codex/urls.py`

### 2. Missing Filtering Support
**Problem:** Django REST Framework couldn't filter garages by operator or cores by garage
**Fixed:**
- Installed `django-filter` package
- Added to `INSTALLED_APPS` and `REST_FRAMEWORK` settings
- Added `filterset_fields` to `GarageView` and `CoreView`

### 3. Garage API Returns Array
**Problem:** `fetchGarageByOperator` expected single object but API returns array
**Fixed:** Updated thunk to extract first element from array

### 4. Old Operators Without Garage
**Problem:** Existing operators created before signal was added don't have garage/cores
**Fixed:** Manually initialized "Maverik" operator with `initialize_operator()`

## Testing Steps

### 1. Backend is Running
```bash
python manage.py runserver
```

### 2. Verify Your Operator
**Current Operator:** Maverik (ID: `6ec6592e-1e70-4f1e-b8c3-6661ecc235d9`)
**Status:** Initialized with garage and starter core

### 3. API Endpoints to Test

```bash
# Check operator (should show bits: 500)
curl http://localhost:8000/codex/operators/6ec6592e-1e70-4f1e-b8c3-6661ecc235d9/

# Check garage (should return one garage)
curl "http://localhost:8000/codex/garages/?operator=6ec6592e-1e70-4f1e-b8c3-6661ecc235d9"

# Check cores (should return Mk-I Frame)
curl "http://localhost:8000/codex/cores/?garage=02d08883-a5ce-4a46-9fcb-4cadf64c70a4&decommed=false"
```

### 4. Frontend Testing

1. **Start Frontend:**
   ```bash
   cd frontend
   npm start
   ```

2. **Login:**
   - Go to http://localhost:3000
   - Click "CONTINUE"
   - Load operator with stored ID (should be Maverik)
   - OR create a new operator (will auto-get garage + starter core)

3. **Check Garage:**
   - Navigate to Garage from main menu
   - You should see:
     - BAY 01: "Mk-I Frame" (Level 1, Common, Balanced)
     - BAY 02: Empty
     - BAY 03: Empty
     - Credits: 500c
     - Core stats displayed when selected

### 5. If Still Not Working

Check browser console for errors:
- Press F12 to open DevTools
- Go to Console tab
- Look for red errors
- Check Network tab to see if API calls are succeeding

Common issues:
- **CORS errors:** Backend CORS settings might need adjustment
- **401 Unauthorized:** Auth context might not have operator ID
- **API not responding:** Check Django server is running on port 8000

## Creating New Test Operators

If you want a fresh operator for testing:

```bash
python manage.py shell
>>> from codex.models import Operator
>>> op = Operator.objects.create(call_sign="YOUR_CALL_SIGN")
>>> print(f"Operator ID: {op.id}")
>>> print(f"Bits: {op.bits}")  # Should be 500
>>> print(f"Has garage: {hasattr(op, 'garage')}")  # Should be True
>>> print(f"Cores: {op.garage.cores.count()}")  # Should be 1
```

The operator ID can be used in localStorage or entered in the "CONTINUE" prompt.
