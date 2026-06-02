# Railway Deployment Guide

## Prerequisites
- Railway account (✅ You have it)
- GitHub account
- This repo pushed to GitHub

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create new repo: `alumnos-coaching-bot`
3. **Do NOT initialize with README** (we have one)

## Step 2: Push Code to GitHub

In your terminal (PowerShell):

```powershell
cd c:\Users\Noxie-PC\Desktop\alumnos_BD

# Initialize git
git init
git add .
git commit -m "Initial coaching system setup - Semana 2 complete"

# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/alumnos-coaching-bot.git
git branch -M main
git push -u origin main
```

## Step 3: Connect to Railway Dashboard

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Authorize Railway to access your GitHub
5. Select `alumnos-coaching-bot` repository
6. Railway auto-detects Dockerfile ✅

## Step 4: Configure Environment Variables

In Railway Dashboard:
1. Go to your project settings
2. Add variables:

```
MONGODB_URI=mongodb+srv://nadir:JxAuNCFVR2LrPI31@alumnosfasttimes.ne7u459.mongodb.net/?appName=Alumnosfasttimes
DB_NAME=Alumnosfasttimes
STRAVA_CLIENT_ID=54106
STRAVA_CLIENT_SECRET=66f94c0d3fbe2e56fd56ed1827971631722d6a69
STRAVA_REDIRECT_URI=https://YOUR-RAILWAY-DOMAIN/callback
TELEGRAM_BOT_TOKEN=8751149434:AAGbt2h2FpAVMKNr-kEg6PSVf0c2ALHMMpo
TELEGRAM_ADMIN_ID=10455209
CLAUDE_API_KEY=[add your key]
OBSIDIAN_VAULT_PATH=/tmp/vault
ENCRYPTION_KEY=ypvGUTdpFNBE2PG974nuM7cmv6MzBvWv9UHJAf8v3Qs=
TIMEZONE=America/Argentina/Buenos_Aires
SYNC_TIME=21:00
```

⚠️ **IMPORTANT:** Railway will give you a public domain. Update `STRAVA_REDIRECT_URI` with that domain.

## Step 5: Deploy

1. Click "Deploy" in Railway Dashboard
2. Wait for build to complete (~3 min)
3. Check logs for errors
4. Service should be running

## Step 6: Test Deployment

1. Get your Railway domain from the dashboard
2. Test Telegram bot with `/start` command
3. Check logs for sync job scheduled
4. Verify MongoDB connection works

## Troubleshooting

**Bot not responding:**
- Check logs in Railway Dashboard
- Verify TELEGRAM_BOT_TOKEN is correct
- Ensure Telegram bot is active with BotFather

**Sync not running at 21:00:**
- Check timezone setting (should be America/Argentina/Buenos_Aires)
- Verify APScheduler logs
- Check MongoDB connection

**Environment variable issues:**
- Re-check all variables copied correctly
- No extra spaces or quotes
- Check special characters in passwords

## Next Steps

1. Register first athlete with `/register` command
2. Complete Strava OAuth flow
3. Wait for 21:00 sync
4. Verify activities synced and Obsidian updated
5. Monitor logs daily

---

**Status:** Ready for deployment  
**Last updated:** 2026-06-01
