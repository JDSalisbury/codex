# CoDEX Login Flow

## Overview

The login system always presents the user with the login screen first, requiring explicit action to enter the game. Operator IDs are persisted in localStorage for convenience but never auto-login.

## User Flow

### First Time Users
1. User visits the app → sees Login screen
2. Selects **"START NEW GAME"**
3. Enters a call sign (operator name)
4. System creates new operator via API
5. Operator ID saved to localStorage and auth context
6. Navigates to Main Menu (`/menu`)

### Returning Users
1. User visits the app → sees Login screen (always)
2. Selects **"CONTINUE"**
3. If operator ID exists in localStorage:
   - Input field auto-fills with stored operator ID
   - Green hint shows: "Previous operator ID found - press LOAD OPERATOR to continue"
4. If no stored operator ID:
   - Input field is empty
   - User manually enters their operator UUID
5. Presses **"LOAD OPERATOR"**
6. System fetches operator from API
7. Operator ID saved to localStorage and auth context
8. Navigates to Main Menu (`/menu`)

### Logout Flow
1. User navigates to System menu
2. Selects **"QUIT GAME"**
3. Confirmation dialog: "Return to main menu?"
4. On confirm:
   - `logout()` called - clears auth context and localStorage
   - Navigates back to Login screen (`/`)
5. User must login again to continue

## Technical Implementation

### AuthContext
- **No auto-login**: Removed automatic operator loading on mount
- **Manual login**: `login(operatorId)` sets context and localStorage
- **Manual logout**: `logout()` clears context and localStorage
- **Helper**: `getStoredOperatorId()` retrieves stored ID without auto-loading

### Login Component
- **Always shows first**: No conditional auto-navigation
- **Smart Continue**: Checks localStorage and pre-fills operator ID when Continue is clicked
- **Explicit action required**: User must click "LOAD OPERATOR" even if ID is pre-filled
- **Visual feedback**: Green hint text shows when stored operator ID is found

### System Component
- **Quit Game**: Calls `logout()` from AuthContext
- **Always returns to login**: Navigates to `/` (Login screen)
- **Clean state**: All operator data cleared on logout

## Routes

- `/` - Login screen (entry point)
- `/menu` - Main Menu (requires authentication)
- `/garage`, `/mission`, `/mail`, `/arena`, `/system` - Game screens (require authentication)

## localStorage Key

- **Key**: `codex_operator_id`
- **Value**: UUID string of the operator
- **Persistence**: Survives browser refresh/close
- **Cleared on**: Logout, or manually by user

## Benefits

1. **Security**: No automatic authentication
2. **Explicit choice**: User decides when to login
3. **Convenience**: Returning users don't need to re-enter UUID
4. **Clean logout**: Proper session termination
5. **Flexibility**: Can manually enter different operator ID if needed
