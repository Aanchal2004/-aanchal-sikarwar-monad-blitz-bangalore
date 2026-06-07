# Deploy Frontend to Vercel

## Quick Deploy

1. Push repo to GitHub
2. Go to [vercel.com](https://vercel.com) → Import Project
3. Set root directory: `frontend`
4. Environment variables:
   - `NEXT_PUBLIC_API_URL` = your backend URL (e.g., Railway/Render)
5. Deploy

## CLI

```bash
cd frontend
npm i -g vercel
vercel
```

## Notes

- Vercel hosts frontend only — deploy backend separately
- Enable CORS on backend for your Vercel domain
- Update `CORS_ORIGINS` in backend `.env`
