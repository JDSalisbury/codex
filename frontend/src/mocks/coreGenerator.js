import { RARITY_PRICES } from "../constants/coreGeneration";

// Helper function to generate random integer between min and max (inclusive)
const randomInt = (min, max) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

// Generate a mock core with random stats
export const generateMockCore = (name, rarity, coreType, tracks = null) => {
  return {
    id: crypto.randomUUID(),
    name: name,
    type: coreType,
    rarity: rarity,
    lvl: 1,
    price: RARITY_PRICES[rarity],
    decommed: false,
    created_at: new Date().toISOString(),
    battle_info: {
      hp: randomInt(90, 130),
      physical: randomInt(8, 16),
      energy: randomInt(8, 16),
      defense: randomInt(8, 16),
      shield: randomInt(0, 20),
      speed: randomInt(6, 14),
      equip_slots: 4,
    },
    upgrade_info: {
      exp: 0,
      next_lvl: 100,
      upgradeable: true,
      tracks: tracks ? [{ name: tracks }] : [],
      lvl_logs: [],
    },
  };
};

// Mock operator data for testing
export const MOCK_OPERATOR = {
  id: "mock-operator-id",
  call_sign: "Test_Pilot",
  bits: 1000,
  premium: 0,
  level: 1,
  rank: "Rookie",
};

// Mock garage data for testing
export const MOCK_GARAGE = {
  id: "mock-garage-id",
  bay_doors: 3,
  core_loadouts: [],
};

// Mock cores list (initial state with starter core)
export const MOCK_CORES = [generateMockCore("Mk-I Frame", "Common", "Balanced")];
