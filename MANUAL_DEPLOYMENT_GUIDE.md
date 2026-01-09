# Manual Web Service Deployment Guide for Render

This guide will help you deploy both services manually as separate web services (free tier available).

## 📋 Prerequisites
- ✅ Repository: `the-fire-detector` on GitHub
- ✅ Render account (free tier works)

## 🚀 Step-by-Step Deployment

### Service 1: FastAPI Service (Fire Detection API)

#### Step 1: Create Web Service
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if not already connected
4. Select repository: `aditya3786/the-fire-detector`
5. Click **"Connect"**

#### Step 2: Configure FastAPI Service

**Basic Settings:**
- **Name**: `fire-detection-api`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: (leave empty)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd platform && python -m uvicorn fastapi_app.main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- Select **"Free"** plan (or Starter if you want always-on)

**Advanced Settings:**
- **Health Check Path**: `/detect/status`

#### Step 3: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

| Key | Value |
|-----|-------|
| `MODEL_PATH` | `weights/best_swapped.pt` |
| `DEVICE` | `cpu` |
| `CONF_THRESHOLD` | `0.10` |
| `IMGSZ` | `512` |
| `ALERT_CONF_THRESHOLD` | `0.50` |
| `WARMUP` | `true` |
| `ALLOW_ORIGINS` | `*` |

#### Step 4: Deploy FastAPI Service
1. Click **"Create Web Service"**
2. Wait for build to complete (5-10 minutes)
3. Note the service URL (e.g., `https://fire-detection-api.onrender.com`)

---

### Service 2: Flask Dashboard Service

#### Step 1: Create Second Web Service
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Select the same repository: `aditya3786/the-fire-detector`
3. Click **"Connect"**

#### Step 2: Configure Flask Service

**Basic Settings:**
- **Name**: `fire-detection-dashboard`
- **Region**: Same as FastAPI service
- **Branch**: `main`
- **Root Directory**: (leave empty)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd platform/backend && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 app:app`

**Plan:**
- Select **"Free"** plan (or Starter if you want always-on)

**Advanced Settings:**
- **Health Check Path**: `/api/health`

#### Step 3: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | (Click "Generate" or use a random string) |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///instance/alerts.db` |
| `FASTAPI_BASE` | `https://fire-detection-api.onrender.com` ⚠️ **Use your actual FastAPI URL** |

**Important**: 
- Replace `fire-detection-api.onrender.com` with your actual FastAPI service URL
- You'll get this URL after FastAPI service is deployed
- If FastAPI isn't deployed yet, deploy it first, then come back and update this

#### Step 4: Deploy Flask Service
1. Click **"Create Web Service"**
2. Wait for build to complete (5-10 minutes)

---

## ✅ Post-Deployment Checklist

### 1. Verify FastAPI Service
- Visit: `https://fire-detection-api.onrender.com/detect/status`
- Should return JSON with model status

### 2. Verify Flask Service
- Visit: `https://fire-detection-dashboard.onrender.com/api/health`
- Should return: `{"status": "healthy", "service": "flask-dashboard"}`

### 3. Update Flask Environment Variable (if needed)
If you set `FASTAPI_BASE` before FastAPI was deployed:
1. Go to Flask service → **"Environment"** tab
2. Update `FASTAPI_BASE` with correct FastAPI URL
3. Service will automatically restart

### 4. Test Full Integration
1. Visit Flask dashboard: `https://fire-detection-dashboard.onrender.com`
2. Try uploading an image
3. Check if detection works and alerts are created

---

## 🔧 Configuration Summary

### FastAPI Service (`fire-detection-api`)
```
Build Command: pip install -r requirements.txt
Start Command: cd platform && python -m uvicorn fastapi_app.main:app --host 0.0.0.0 --port $PORT
Health Check: /detect/status
```

### Flask Service (`fire-detection-dashboard`)
```
Build Command: pip install -r requirements.txt
Start Command: cd platform/backend && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 app:app
Health Check: /api/health
```

---

## ⚠️ Important Notes

### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Build time: 5-10 minutes per service

### Service URLs
After deployment, you'll have:
- **FastAPI**: `https://fire-detection-api-XXXX.onrender.com`
- **Flask**: `https://fire-detection-dashboard-XXXX.onrender.com`

The `XXXX` part is unique to your account.

### Database
- Currently using SQLite (ephemeral on free tier)
- Data may be lost when service restarts
- For production, consider PostgreSQL (Render offers free PostgreSQL)

---

## 🐛 Troubleshooting

### Build Fails
- Check build logs for specific errors
- Verify Python version (Render uses 3.9+)
- Ensure all dependencies in requirements.txt are correct

### Services Can't Communicate
- Verify `FASTAPI_BASE` in Flask service matches FastAPI URL exactly
- Check that FastAPI service is running
- Ensure CORS is enabled (`ALLOW_ORIGINS: *`)

### Model Not Found
- Verify `weights/best_swapped.pt` exists in repository
- Check `MODEL_PATH` environment variable
- Model will fallback to `yolov8n.pt` if custom model not found

### Service Spins Down
- This is normal on free tier
- First request after spin-down is slow
- Consider upgrading to Starter plan ($7/month) for always-on

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Check service logs in Render dashboard
- Review build logs for specific errors
