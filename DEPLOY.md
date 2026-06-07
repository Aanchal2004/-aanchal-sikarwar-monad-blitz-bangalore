# AgentMandi — Deploy (Vercel + Render)

## Overview

| Service | Host | URL pattern |
|---------|------|-------------|
| Frontend | [Vercel](https://vercel.com) | `https://your-app.vercel.app` |
| Backend | [Render](https://render.com) | `https://agentmandi-api.onrender.com` |

Both must use **HTTPS** so WebSockets work (`wss://`).

---

## Step 1 — Backend on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect repo: `Aanchal2004/-aanchal-sikarwar-monad-blitz-bangalore`
3. Settings:
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
4. Add **Environment Variables** (from your local `backend/.env`):

   | Key | Value |
   |-----|-------|
   | `PYTHON_VERSION` | `3.12.8` |
   | `MANAGER_PRIVATE_KEY` | your manager private key |
   | `MANAGER_ADDRESS` | `0xa95c36aa4Cfd8C82daCC33788B09ba214bE1d358` |
   | `AGENTMANDI_CONTRACT_ADDRESS` | from `.env` |
   | `SARVAM_API_KEY` | your Sarvam key |
   | `MONAD_RPC_URL` | `https://testnet-rpc.monad.xyz` |
   | `MONAD_CHAIN_ID` | `10143` |
   | `LLM_PROVIDER` | `sarvam` |
   | `SCRIPTED_RATINGS` | `true` |
   | `CORS_ORIGINS` | `*` |

5. Add **`WALLETS_JSON`** — paste entire contents of `backend/wallets.json` as one line (Render supports multiline env vars).

6. Deploy → wait for **Live** → test:
   ```
   https://YOUR-SERVICE.onrender.com/health
   ```
   Expect `chain_ready: true` and balance > 0.

**Note:** Render free tier sleeps after ~15 min idle. First request may take ~30s. Use [UptimeRobot](https://uptimerobot.com) to ping `/health` every 10 min during the demo.

---

## Step 2 — Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Import the same GitHub repo
3. Settings:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Next.js
4. **Environment Variable** (Production):

   ```
   NEXT_PUBLIC_BACKEND_URL=https://YOUR-SERVICE.onrender.com
   ```

   No trailing slash. Must be set **before** the first build.

5. Deploy → open `https://your-app.vercel.app/console`

---

## Step 3 — Smoke test

1. `/console` → submit D2C demo prompt, budget `0.60`
2. WebSocket panel updates live
3. `/agents` → 4 providers listed
4. Run completes → **View full run receipt**

---

## CORS troubleshooting

- Backend `CORS_ORIGINS=*` allows all REST origins
- WebSocket connects directly to Render URL (`wss://...`)
- If frontend shows network errors, verify `NEXT_PUBLIC_BACKEND_URL` matches Render URL exactly (https, no trailing slash)
- Redeploy Vercel after changing `NEXT_PUBLIC_BACKEND_URL`

---

## Optional — CLI deploy

```powershell
# Vercel (from frontend/)
npx vercel --prod
# Set NEXT_PUBLIC_BACKEND_URL in Vercel dashboard first

# Render: use dashboard or render.yaml blueprint
```

---

## Files committed for deploy

- `backend/app/contract_abi.json` — public ABI (safe to commit)
- `render.yaml` — Render blueprint
- `frontend/vercel.json` — Vercel config
- `WALLETS_JSON` env — wallets stay out of git
