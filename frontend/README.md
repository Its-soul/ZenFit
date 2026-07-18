# ZenFit Frontend

This folder is the self-contained Next.js web application. Routes live in `app/`, reusable UI in `components/`, API clients in `services/`, and shared browser utilities in `lib/` and `hooks/`.

```powershell
npm install
npm run dev
npm run lint
npm run build
```

Required public configuration:

```env
NEXT_PUBLIC_API_URL=https://your-backend.example/api/v1
NEXT_PUBLIC_WS_URL=wss://your-backend.example/ws
```

For Vercel, set Root Directory to `frontend/`. The frontend communicates with the backend only through configured HTTP/WebSocket URLs and does not require backend source files at runtime.
