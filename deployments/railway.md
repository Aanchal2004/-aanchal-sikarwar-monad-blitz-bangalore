# Deploy to Railway

## Full Stack (Backend + Frontend)

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Add two services from same repo:

### Backend Service
- Root: `/backend`
- Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Variables: copy from `.env.example`

### Frontend Service
- Root: `/frontend`
- Build: `npm install && npm run build`
- Start: `npm start`
- Variable: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`

## Single Dockerfile

```bash
railway up
# Uses docker-compose.yml if configured
```

## Hackathon Tip

Railway is fastest for full-stack demo — both services in one project, shared env management.
