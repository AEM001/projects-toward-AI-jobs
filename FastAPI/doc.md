cd /Users/Mac/code/project/FastAPI/cloud
python -m uvicorn src.core.main:app --reload --host 0.0.0.0 --port 8000

cd /Users/Mac/code/project/FastAPI/frontend
npm run dev

Access the app:

Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs

frontend/
├── src/
│   ├── app/                    # Pages (file-based routing)
│   │   ├── page.tsx            # Home (redirects)
│   │   ├── login/page.tsx      # Login page
│   │   ├── register/page.tsx   # Register page
│   │   └── todos/page.tsx      # Todos page
│   ├── components/ui/          # shadcn/ui components
│   ├── services/api.ts         # API client
│   ├── store/authStore.ts      # Auth state (Zustand)
│   └── types/index.ts          # TypeScript types
├── FRONTEND_GUIDE.md           # 📚 Complete beginner guide
└── .env.local                  # API URL configuration