// frontend/src/services/battleWebSocket.js
/**
 * WebSocket service for real-time battle communication.
 */

const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

class BattleWebSocketService {
  constructor() {
    this.socket = null;
    this.dispatch = null;
    this.battleId = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  /**
   * Connect to a battle websocket.
   * @param {string} battleId - The battle UUID
   * @param {function} dispatch - Redux dispatch function
   * @param {object} actions - Redux action creators
   */
  connect(battleId, dispatch, actions) {
    this.battleId = battleId;
    this.dispatch = dispatch;
    this.actions = actions;

    const url = `${WS_BASE_URL}/ws/battle/${battleId}/`;

    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log('Battle WebSocket connected');
      this.reconnectAttempts = 0;
      dispatch(actions.setConnected(true));

      // Request initial battle state
      this.send({ type: 'battle_init' });
    };

    this.socket.onmessage = (event) => {
      this.handleMessage(event);
    };

    this.socket.onclose = (event) => {
      console.log('Battle WebSocket closed:', event.code);
      dispatch(actions.setConnected(false));

      // Attempt reconnect if not a normal close
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
        setTimeout(() => {
          this.connect(battleId, dispatch, actions);
        }, this.reconnectDelay * this.reconnectAttempts);
      }
    };

    this.socket.onerror = (error) => {
      console.error('Battle WebSocket error:', error);
      dispatch(actions.setError('WebSocket connection error'));
    };
  }

  /**
   * Disconnect from the websocket.
   */
  disconnect() {
    if (this.socket) {
      this.socket.close(1000, 'Client disconnect');
      this.socket = null;
    }
    this.battleId = null;
    this.dispatch = null;
  }

  /**
   * Send a message to the server.
   * @param {object} data - The message data
   */
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.error('WebSocket not connected');
    }
  }

  /**
   * Send a player action (move, switch, pass, gain_resource).
   * @param {string} actionType - 'move' | 'switch' | 'pass' | 'gain_resource'
   * @param {object} actionData - Additional action data
   */
  sendAction(actionType, actionData = {}) {
    this.send({
      type: 'action',
      action_type: actionType,
      action_data: actionData,
    });
  }

  /**
   * Send dice allocation.
   * @param {array} allocations - [{core_id, pool}, ...]
   */
  sendDiceAllocation(allocations) {
    this.send({
      type: 'dice_allocation',
      allocations,
    });
  }

  /**
   * Handle incoming websocket messages.
   * @param {MessageEvent} event - The websocket message event
   */
  handleMessage(event) {
    const data = JSON.parse(event.data);
    const { dispatch, actions } = this;

    if (!dispatch || !actions) return;

    switch (data.type) {
      case 'connection_established':
        console.log('Connection established for battle:', data.battle_id);
        break;

      case 'battle_state':
        dispatch(actions.setBattleState(data));
        break;

      case 'turn_start':
        dispatch(actions.setTurnStart(data));
        break;

      case 'resource_dice':
        dispatch(actions.setResourceDice(data));
        break;

      case 'dice_allocated':
        dispatch(actions.setDiceAllocated(data));
        break;

      case 'action_result':
        dispatch(actions.setActionResult(data));
        break;

      case 'action_rejected':
        dispatch(actions.setActionRejected(data));
        break;

      case 'forced_switch':
        dispatch(actions.setForcedSwitch(data));
        break;

      case 'battle_end':
        dispatch(actions.setBattleEnd(data));
        break;

      case 'error':
        dispatch(actions.setError(data.message));
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  }
}

// Singleton instance
const battleWebSocket = new BattleWebSocketService();

export default battleWebSocket;
