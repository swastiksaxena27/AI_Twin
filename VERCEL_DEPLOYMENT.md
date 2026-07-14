# Deploying AI Behavioral Guardian with Vercel + Render

To deploy this application, we use a hybrid hosting setup:
1. **Frontend (React)**: Deployed to **Vercel** (fast, free, static hosting).
2. **Backend (FastAPI)**: Deployed to **Render** (persistent Python hosting supporting SQLite database writes).

> [!IMPORTANT]
> Do not attempt to run the backend on Vercel. Vercel Serverless Functions run on a read-only filesystem, which will crash the SQLite database initialization and prevent saving users or logs.

---

## 🎨 Phase 1: Deploy Frontend on Vercel

### Option A: Via GitHub (Recommended)
1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "Configure Vercel deployment"
   git push origin main
   ```
2. Log in to [vercel.com](https://vercel.com) using your GitHub account.
3. Click **Add New** -> **Project**.
4. Import your `ai-behavioral-guardian` repository.
5. In the **Configure Project** settings:
   - **Framework Preset**: Vite
   - **Root Directory**: Click `Edit` and select `frontend`.
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. Expand **Environment Variables** and add:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://your-backend-url.onrender.com/api/v1` *(You can update this later once your backend is running)*
7. Click **Deploy**.

### Option B: Via Vercel CLI
If you want to deploy directly from your local terminal:
```bash
# Install Vercel CLI globally
npm install -g vercel

# Run vercel inside the frontend directory
cd frontend
vercel
```
Follow the interactive prompts to link and deploy the frontend.

---

## 🐍 Phase 2: Deploy Backend on Render

Since we removed the blueprint `render.yaml` to clean up the repository, you can manually set up the backend on Render in a few clicks:

1. Go to [render.com](https://render.com) and log in.
2. Click **New** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following configuration details:
   - **Name**: `ai-behavioral-guardian-backend`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn behavioral_guardian.backend.main:app --host 0.0.0.0 --port $PORT`
5. Click **Advanced** and add the following Environment Variables:
   - `BEHAVIORAL_GUARDIAN_JWT_SECRET` : *(Generate a secure random string)*
   - `PYTHON_VERSION` : `3.12.3`
6. Click **Create Web Service**.

---

## 🔗 Phase 3: Link Them Together

Once your Render backend is live, copy its URL (e.g., `https://ai-behavioral-guardian-backend.onrender.com`) and:
1. Go to your Vercel Dashboard -> **ai-behavioral-guardian-frontend** -> **Settings** -> **Environment Variables**.
2. Edit `VITE_API_BASE_URL` and set it to:
   `https://your-backend-url.onrender.com/api/v1`
3. Redeploy your production deployment on Vercel to bake in the new URL.
