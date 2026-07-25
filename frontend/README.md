# ZenFit Frontend

This folder is the production Next.js web application. Routes live in `app/`, reusable UI in `components/`, API clients in `services/`, and shared browser utilities in `lib/` and `hooks/`.

The generated `../ZEN-FRONT` app is a visual reference only. Do not replace this folder with it; migrate pages incrementally and keep the existing API/auth contracts.

## Commands

```powershell
npm install
npm run dev
npm run lint
npm run build
```

## Environment

```env
NEXT_PUBLIC_API_URL=https://your-backend.example/api/v1
NEXT_PUBLIC_WS_URL=wss://your-backend.example/ws
```

## Structure

```text
frontend/
├── app/          # Next.js App Router pages
├── components/   # Landing, layout, product, common, and UI components
├── hooks/        # Auth and realtime hooks
├── lib/          # Runtime config, auth storage, and shared helpers
├── public/       # Static production assets
└── services/     # Centralized backend API clients
```

## Deployment

For Vercel, set Root Directory to `frontend/`. The frontend communicates with the backend only through configured HTTP/WebSocket URLs and does not require backend source files at runtime.

The landing page uses `public/assets/main-bg.mp4`, copied from `../ZEN-FRONT/src/MAIN-BG.mp4`, as an animated background with a reduced-motion fallback.
