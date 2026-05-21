# 🚀 NexusFlow AI — Complete Deployment Guide

> **This guide is written for absolute beginners.**
> Follow each step in order. Every step has a ✅ checkbox so you know what's done.

---

## What You're Building

You're going to deploy three things:

1. **The database** — where all your data lives (on Neon — free)
2. **The backend API** — the brain of the app (on Render — free)
3. **The website / dashboard** — the beautiful UI (on Vercel — free)

---

## Before You Start — Accounts You Need

Create free accounts at these websites first (keep the browser tabs open):

| Service    | URL                   | What It Does                    |
| ---------- | --------------------- | ------------------------------- |
| Neon       | https://neon.tech     | Database + User login           |
| Upstash    | https://upstash.com   | Fast real-time events           |
| Inngest    | https://inngest.com   | Background jobs                 |
| OpenRouter | https://openrouter.ai | AI models (GPT-4, Claude, etc.) |
| Render     | https://render.com    | Hosts your backend              |
| Vercel     | https://vercel.com    | Hosts your website              |
| GitHub     | https://github.com    | Where your code lives           |

---

## Step 1 — Push Code to GitHub

> Think of GitHub as a safe locker for your code.

1. Go to https://github.com/new
2. Create a new repository. Call it `nexusflow`
3. Make it **Private**
4. Open your terminal (Command Prompt on Windows, Terminal on Mac)
5. Go to your project folder:
   ```
   cd d:\workFiles\nexusflow
   ```
6. Run these commands one by one:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/nexusflow.git
   git push -u origin main
   ```

✅ Your code is now on GitHub!

---

## Step 2 — Set Up Your Database on Neon

> Neon is like a giant spreadsheet that stores all your users, workflows, and data.

1. Go to https://console.neon.tech
2. Click **"New Project"**
3. Name it `nexusflow` and click Create
4. You'll see a **Connection String** — it looks like:
   ```
   postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
   👉 **Copy this somewhere safe — you'll need it later!**
5. Click on the **"SQL Editor"** tab
6. Run this command to enable the AI search feature:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
7. Click **Run**

✅ Your database is ready!

---

## Step 3 — Set Up User Login (Neon Auth)

> This lets users sign up and sign in with email or Google.

1. Still on https://console.neon.tech, look in the left sidebar for **"Auth"**
2. Click it, then click **"Enable Auth"** (or "Get Started")
3. Open **Auth → Configuration** and copy your **Auth URL**. It looks like:
   ```
   https://ep-xxx.neonauth.us-east-2.aws.neon.tech/neondb/auth
   ```
4. Generate a cookie secret for the Next.js app. Run this in your terminal:
   ```bash
   openssl rand -base64 32
   ```
   Save the output somewhere safe. You will use it later as `NEON_AUTH_COOKIE_SECRET`.
5. Still on the Auth page, scroll to **"OAuth Providers"** if you want Google login:
   - Toggle Google ON
   - You'll need to create OAuth credentials at https://console.cloud.google.com (optional — email login works without this)
6. After your Vercel site is live, come back and add your production frontend URL in **Auth → Configuration**:
   - **Allowed origins / App URLs**:
   ```
   https://your-app.vercel.app
   ```

   - If you use Google or another OAuth provider, also add:
   ```
   https://your-app.vercel.app/auth/callback
   ```
   If you skip the production frontend origin, sign-up/sign-in requests fail with `INVALID_ORIGIN`.

✅ User login is configured!

---

## Step 4 — Set Up Upstash Redis

> Upstash is like a fast messenger that sends real-time updates to your browser.

1. Go to https://console.upstash.com
2. Click **"Create Database"**
3. Name it `nexusflow`, choose **Regional** type
4. Pick a region close to you (e.g., US East 1)
5. Click Create
6. On the database page, scroll down to **"REST API"** section
7. Copy the **URL** and **Token** — they look like:
   - URL: `https://example-12345.upstash.io`
   - Token: `AXxxxxxxxxxxxxxxxxxxx==`

✅ Real-time events are ready!

---

## Step 5 — Set Up Inngest (Background Jobs)

> Inngest handles long-running tasks (like processing documents) without slowing down your app.

1. Go to https://app.inngest.com
2. Sign up and create a new application
3. Name it `nexusflow-ai`
4. In the app settings, find and copy:
   - **Event Key** — looks like `evt_xxxxx`
   - **Signing Key** — looks like `signkey-prod-xxxxx`
5. After you deploy your backend (Step 7), come back and register your app:
   - Go to **"Apps"** → **"Connect an app"**
   - URL: `https://nexusflow-api.onrender.com/inngest`

✅ Background jobs are set up!

---

## Step 6 — Get Your AI API Key (OpenRouter)

> OpenRouter lets you use GPT-4, Claude, Gemini, and more — all with one key.

1. Go to https://openrouter.ai
2. Sign up (free)
3. Go to https://openrouter.ai/keys
4. Click **"Create Key"** — name it `nexusflow`
5. Copy the key — it starts with `sk-or-v1-`
6. Add **$5 of credits** (this will last a very long time with GPT-4o Mini!)
   - Click "Credits" → "Add Credits" → pay with card

✅ AI is powered up!

---

## Step 7 — Deploy the Backend to Render

> Render will run your Python backend 24/7 for free.

### 7a. Create the backend service

1. Go to https://render.com
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub account if you haven't already
4. Select your `nexusflow` repository
5. Fill in the settings:
   - **Name**: `nexusflow-api`
   - **Region**: Choose one close to you
   - **Branch**: `main`
   - **Root Directory**: `apps/api`
   - **Runtime**: `Docker` (Render will detect the Dockerfile automatically)
   - **Instance Type**: `Free`

### 7b. Add environment variables

Scroll down to **"Environment Variables"** and add each of these:

| Variable Name              | Value                                                |
| -------------------------- | ---------------------------------------------------- |
| `DATABASE_URL`             | Your Neon connection string from Step 2              |
| `NEON_AUTH_JWKS_URL`       | Your Auth URL from Step 3 + `/.well-known/jwks.json` |
| `UPSTASH_REDIS_REST_URL`   | Your Upstash URL from Step 4                         |
| `UPSTASH_REDIS_REST_TOKEN` | Your Upstash token from Step 4                       |
| `OPENROUTER_API_KEY`       | Your OpenRouter key from Step 6                      |
| `INNGEST_EVENT_KEY`        | Your Inngest event key from Step 5                   |
| `INNGEST_SIGNING_KEY`      | Your Inngest signing key from Step 5                 |
| `FRONTEND_URL`             | `https://your-app.vercel.app` (update after Step 8!) |
| `SECRET_KEY`               | A random 32-character string (generate below)        |

**To generate a SECRET_KEY**, run this in your terminal:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as the `SECRET_KEY` value.

### 7c. Click Deploy!

1. Click **"Create Web Service"**
2. Wait for the build to finish (takes ~5 minutes the first time — watch the logs!)
3. When you see ✅ **"Deploy live"**, your backend is running!
4. Copy your backend URL — it looks like `https://nexusflow-api.onrender.com`

### 7d. Run database migrations

> This creates all the tables in your database.

1. In Render, click on your service → **"Shell"** tab
2. Type this command and press Enter:
   ```bash
   alembic upgrade head
   ```
3. You should see output ending with `Running upgrade ... -> ...`

✅ Backend is live! Test it at: `https://nexusflow-api.onrender.com/health`

---

## Step 8 — Deploy the Frontend to Vercel

> Vercel hosts your Next.js website instantly with zero config.

### 8a. Import your project

1. Go to https://vercel.com
2. Click **"Add New"** → **"Project"**
3. Click **"Import"** next to your `nexusflow` repository
4. Configure the project:
   - **Framework**: Next.js (auto-detected)
   - **Root Directory**: `apps/web`

### 8b. Add environment variables

Click **"Environment Variables"** and add:

| Variable Name             | Value                                       |
| ------------------------- | ------------------------------------------- |
| `NEXT_PUBLIC_API_URL`     | `https://nexusflow-api.onrender.com/api/v1` |
| `NEON_AUTH_BASE_URL`      | Your Auth URL from Step 3                   |
| `NEON_AUTH_COOKIE_SECRET` | The secret you generated in Step 3          |
| `BLOB_READ_WRITE_TOKEN`   | See Step 8c below                           |

### 8c. Set up Vercel Blob (file storage)

1. In Vercel, go to **"Storage"** tab in your dashboard
2. Click **"Create Database"** → **"Blob"**
3. Name it `nexusflow-storage`
4. Connect it to your project
5. Vercel automatically adds `BLOB_READ_WRITE_TOKEN` to your environment!

### 8d. Deploy!

1. Click **"Deploy"**
2. Wait ~2 minutes for the build
3. Your app is live at `https://nexusflow-SOMETHING.vercel.app`!

✅ Frontend is live!

---

## Step 9 — Connect Everything Together

Now update a few settings with your real URLs:

### 9a. Update CORS on the backend

1. In Render, go to your service → **"Environment"**
2. Update `FRONTEND_URL` to your actual Vercel URL (e.g., `https://nexusflow-abc.vercel.app`)
3. Click **"Save Changes"** → Render will redeploy automatically

### 9b. Update Neon Auth production URLs

1. Go back to https://console.neon.tech → **Auth** → **Configuration**
2. Add your real Vercel URL to **Allowed origins / App URLs**:
   ```
   https://nexusflow-abc.vercel.app
   ```
3. If you enabled Google or another OAuth provider, also add:
   ```
   https://nexusflow-abc.vercel.app/auth/callback
   ```

### 9c. Register Inngest app

1. Go to https://app.inngest.com → **"Apps"**
2. Click **"Connect an App"**
3. Enter URL: `https://nexusflow-api.onrender.com/inngest`
4. Click **"Connect"**

✅ Everything is wired together!

---

## Step 10 — Test Your Deployment

1. Open your Vercel URL in the browser
2. Click **"Get Started Free"** and sign up
3. Verify your email (Neon Auth sends a confirmation email)
4. You're in! Try creating a workflow in the dashboard.

**Test the backend directly:**

- `https://nexusflow-api.onrender.com/health` → should return `{"status": "ok"}`
- `https://nexusflow-api.onrender.com/docs` → interactive API docs (Swagger UI)

---

## ⚠️ Important: Keep the Backend Awake

Render's free tier **sleeps after 15 minutes** of no traffic. The first request after sleeping takes ~30 seconds.

**Solution:** Add a "keep-alive" ping. Go to https://cron-job.org (free), create a cron job that hits `https://nexusflow-api.onrender.com/health` every **14 minutes**.

---

## 🔧 Troubleshooting

| Problem                             | Fix                                                                                           |
| ----------------------------------- | --------------------------------------------------------------------------------------------- |
| Backend returns 500                 | Check Render logs → **Logs** tab                                                              |
| `INVALID_ORIGIN` on sign-up/sign-in | Add your exact Vercel URL in Neon → **Auth** → **Configuration** → Allowed origins / App URLs |
| Login doesn't work                  | Check `NEON_AUTH_BASE_URL` and `NEON_AUTH_COOKIE_SECRET` in Vercel                            |
| "CORS error" in browser             | Make sure `FRONTEND_URL` in Render matches your exact Vercel URL                              |
| Document upload fails               | Make sure Vercel Blob is connected and `BLOB_READ_WRITE_TOKEN` is set                         |
| AI agents don't respond             | Check `OPENROUTER_API_KEY` is correct and has credits                                         |
| Database error                      | Re-run `alembic upgrade head` in Render shell                                                 |

---

## 📋 Final Checklist

- [ ] Code pushed to GitHub
- [ ] Neon database created + vector extension enabled
- [ ] Neon Auth configured with callback URLs
- [ ] Upstash Redis created
- [ ] Inngest app created
- [ ] OpenRouter API key with credits
- [ ] Backend deployed on Render with all env vars
- [ ] `alembic upgrade head` ran in Render shell
- [ ] Frontend deployed on Vercel with all env vars
- [ ] Vercel Blob connected
- [ ] `FRONTEND_URL` updated on Render
- [ ] Inngest app connected to backend URL
- [ ] Keep-alive cron job set up on cron-job.org
- [ ] Test login + workflow creation works

**🎉 You're live! Share your app URL with the world.**

---

## 💰 Cost Summary (All Free!)

| Service    | Free Tier Limits                                   |
| ---------- | -------------------------------------------------- |
| Neon       | 0.5 GB storage, 1 project                          |
| Render     | 750 hours/month (enough for 1 service)             |
| Vercel     | 100 GB bandwidth, unlimited deploys                |
| Upstash    | 10,000 requests/day, 256 MB                        |
| Inngest    | 50,000 function runs/month                         |
| OpenRouter | Pay as you go (GPT-4o Mini = ~$0.15 per 1M tokens) |

> Total monthly cost to run NexusFlow AI: **$0** (unless you exceed the OpenRouter credits you added)
