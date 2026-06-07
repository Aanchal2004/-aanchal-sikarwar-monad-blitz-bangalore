# Deploy Backend to Render

## Steps

1. Create account at [render.com](https://render.com)
2. New → Web Service → Connect GitHub repo
3. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.12
4. Add env vars from `.env.example`
5. Deploy

## render.yaml (optional)

```yaml
services:
  - type: web
    name: monad-agent-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: LLM_PROVIDER
        value: openai
      - key: OPENAI_API_KEY
        sync: false
```

## Notes

- Free tier sleeps after inactivity — wake before demo
- Copy Render URL to frontend `NEXT_PUBLIC_API_URL`
