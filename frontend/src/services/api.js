const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000/codex";
const BATTLE_API_BASE_URL =
  process.env.REACT_APP_BATTLE_API_URL || "http://localhost:8000/battle";

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.battleURL = BATTLE_API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ detail: "Request failed" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("API Request failed:", error);
      throw error;
    }
  }

  async battleRequest(endpoint, options = {}) {
    const url = `${this.battleURL}${endpoint}`;
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response
          .json()
          .catch(() => ({ detail: "Request failed" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Battle API Request failed:", error);
      throw error;
    }
  }

  // Operator endpoints
  async getOperator(operatorId) {
    return this.request(`/operators/${operatorId}/`);
  }

  async createOperator(data) {
    return this.request("/operators/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateOperator(operatorId, data) {
    return this.request(`/operators/${operatorId}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  // Garage endpoints
  async getGarage(garageId) {
    return this.request(`/garages/${garageId}/`);
  }

  async getGarageByOperator(operatorId) {
    return this.request(`/garages/?operator=${operatorId}`);
  }

  async updateGarage(garageId, data) {
    return this.request(`/garages/${garageId}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  // Core endpoints
  async getCores(garageId) {
    return this.request(`/cores/?garage=${garageId}&decommed=false`);
  }

  async getCore(coreId) {
    return this.request(`/cores/${coreId}/`);
  }

  async generateCore(data) {
    return this.request("/cores/generate/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateCore(coreId, data) {
    return this.request(`/cores/${coreId}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async decommissionCore(coreId) {
    return this.request(`/cores/${coreId}/decommission/`, {
      method: "POST",
    });
  }

  // Core Battle Info endpoints
  async getCoreBattleInfo(coreId) {
    return this.request(`/cores/${coreId}/battle_info/`);
  }

  // Core Upgrade Info endpoints
  async getCoreUpgradeInfo(coreId) {
    return this.request(`/cores/${coreId}/upgrade_info/`);
  }

  // Move endpoints
  async getMoves(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/moves/${queryString ? `?${queryString}` : ""}`);
  }

  async getMove(moveId) {
    return this.request(`/moves/${moveId}/`);
  }

  // Core Equipped Moves endpoints
  async getCoreEquippedMoves(coreId) {
    return this.request(`/cores/${coreId}/equipped-moves/`);
  }

  async getCoreAvailableMoves(coreId) {
    return this.request(`/cores/${coreId}/available-moves/`);
  }

  async equipMove(coreId, moveId, slot) {
    return this.request(`/cores/${coreId}/equip-move/`, {
      method: "POST",
      body: JSON.stringify({ move_id: moveId, slot }),
    });
  }

  async unequipMove(coreId, slot) {
    return this.request(`/cores/${coreId}/unequip-move/`, {
      method: "POST",
      body: JSON.stringify({ slot }),
    });
  }

  // Scrapyard endpoints
  async getScrapyard() {
    return this.request("/scrapyard/00000000-0000-0000-0000-000000000001/");
  }

  async getDecommissionedCores() {
    return this.request("/scrapyard/decommissioned-cores/");
  }

  async recommissionCore(coreId) {
    return this.request(`/cores/${coreId}/recommission/`, {
      method: "POST",
    });
  }

  async getMoveShop() {
    return this.request("/scrapyard/move-shop/");
  }

  async purchaseMove(coreId, moveId) {
    return this.request(`/cores/${coreId}/purchase-move/`, {
      method: "POST",
      body: JSON.stringify({ move_id: moveId }),
    });
  }

  // Equipment endpoints
  async getEquipment(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/equipment/${queryString ? `?${queryString}` : ""}`);
  }

  async getEquipmentItem(equipmentId) {
    return this.request(`/equipment/${equipmentId}/`);
  }

  // Mail endpoints (Battle API)
  async getMail(operatorId) {
    return this.battleRequest(`/mail/?operator=${operatorId}`);
  }

  async getMailDetail(mailId) {
    return this.battleRequest(`/mail/${mailId}/`);
  }

  async markMailRead(mailId) {
    return this.battleRequest(`/mail/${mailId}/mark-read/`, {
      method: "POST",
    });
  }

  async getUnreadCount(operatorId) {
    return this.battleRequest(`/mail/unread-count/?operator=${operatorId}`);
  }

  // Arena endpoints (Battle API)
  async getArenaNPCs(rank = 'E', operatorId = null) {
    const params = operatorId ? `?operator=${operatorId}` : '';
    return this.battleRequest(`/arena/by-rank/${rank}/${params}`);
  }

  async getNPCDetail(npcId, operatorId = null) {
    const params = operatorId ? `?operator=${operatorId}` : '';
    return this.battleRequest(`/arena/${npcId}/${params}`);
  }

  async getArenaProgress(operatorId) {
    return this.battleRequest(`/arena/progress/?operator=${operatorId}`);
  }

  async challengeNPC(npcId, operatorId, outcome) {
    return this.battleRequest(`/arena/${npcId}/challenge/`, {
      method: 'POST',
      body: JSON.stringify({ operator_id: operatorId, outcome }),
    });
  }

  async startBattle(npcId, operatorId) {
    return this.battleRequest(`/arena/${npcId}/start-battle/`, {
      method: 'POST',
      body: JSON.stringify({ operator_id: operatorId }),
    });
  }
}

export default new ApiService();
