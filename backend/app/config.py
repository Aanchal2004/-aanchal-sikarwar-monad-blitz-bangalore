"""Central config loaded from environment (.env)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

# --- Monad ---
MONAD_RPC_URL = os.getenv("MONAD_RPC_URL", "https://testnet-rpc.monad.xyz")
MONAD_CHAIN_ID = int(os.getenv("MONAD_CHAIN_ID", "10143"))
EXPLORER_TX_BASE = "https://testnet.monadscan.com/tx/"
EXPLORER_ADDR_BASE = "https://testnet.monadscan.com/address/"

CONTRACT_ADDRESS = os.getenv("AGENTMANDI_CONTRACT_ADDRESS", "").strip()

# --- Manager wallet (owner + sole sender) ---
MANAGER_PRIVATE_KEY = os.getenv("MANAGER_PRIVATE_KEY", "").strip()
MANAGER_ADDRESS = os.getenv("MANAGER_ADDRESS", "").strip()

# --- LLM ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "sarvam").strip().lower()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "").strip()
SARVAM_CHAT_MODEL = os.getenv("SARVAM_CHAT_MODEL", "sarvam-105b").strip()
SARVAM_WORK_MODEL = os.getenv("SARVAM_WORK_MODEL", "sarvam-30b").strip()
SARVAM_BASE_URL = "https://api.sarvam.ai/v1/chat/completions"

# --- Demo behavior ---
SCRIPTED_RATINGS = os.getenv("SCRIPTED_RATINGS", "true").strip().lower() == "true"

# --- Paths ---
DB_PATH = BACKEND_DIR / "agentmandi.db"
WALLETS_PATH = BACKEND_DIR / "wallets.json"
ABI_PATH = BACKEND_DIR / "app" / "contract_abi.json"
