# Deploy with Docker

## Local

```bash
cp .env.example .env
# Edit .env with API keys
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

## Production

```bash
docker compose -f docker-compose.yml up -d
```

## Backend Only

```bash
docker build -f backend/Dockerfile -t monad-agent-api .
docker run -p 8000:8000 --env-file .env monad-agent-api
```

## Frontend Only

Note: Frontend Dockerfile uses standalone output. Add to `next.config.ts`:

```typescript
const nextConfig = { output: "standalone" };
```

Then rebuild.

## Troubleshooting

- CORS errors → set `CORS_ORIGINS` to frontend URL
- Module not found → check `PYTHONPATH` in backend Dockerfile
- Mock responses → verify API keys in container env
