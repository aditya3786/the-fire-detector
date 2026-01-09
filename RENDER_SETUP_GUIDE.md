# 🚀 Render Deployment - Step by Step Guide

## ✅ Prerequisites Completed
- ✅ Repository created: `the-fire-detector`
- ✅ Code pushed to GitHub
- ✅ All deployment files in place

## 📋 Deployment Steps

### Step 1: Sign Up / Log In to Render
1. Go to https://render.com
2. Sign up or log in (you can use GitHub to sign in)
3. Verify your account if needed

### Step 2: Deploy Using Blueprint (Easiest Method)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Click the **"New +"** button (top right)
   - Select **"Blueprint"**

2. **Connect Your Repository**
   - Click **"Connect account"** if you haven't connected GitHub
   - Select your repository: `aditya3786/the-fire-detector`
   - Click **"Connect"**

3. **Review Services**
   - Render will automatically detect `render.yaml`
   - You should see 2 services:
     - `fire-detection-api` (FastAPI)
     - `fire-detection-dashboard` (Flask)
   - Review the configuration
   - **Important**: Make sure both services are set to **"Starter"** plan (or Free if available)

4. **Deploy**
   - Click **"Apply"** at the bottom
   - Render will start building both services

### Step 3: Monitor Deployment

1. **Watch Build Logs**
   - Click on each service to see build progress
   - FastAPI service will build first
   - Flask service will build after

2. **Check for Errors**
   - Look for any build failures
   - Common issues:
     - Missing dependencies (check requirements.txt)
     - Model file not found (verify weights/ directory)
     - Port configuration issues

3. **Verify Health Checks**
   - Once deployed, check:
     - FastAPI: `https://fire-detection-api.onrender.com/detect/status`
     - Flask: `https://fire-detection-dashboard.onrender.com/api/health`

### Step 4: Configure Flask Service (After FastAPI is Live)

1. **Get FastAPI URL**
   - Once FastAPI service is live, copy its URL
   - Example: `https://fire-detection-api.onrender.com`

2. **Update Flask Environment Variable**
   - Go to Flask service settings
   - Navigate to **"Environment"** tab
   - Find `FASTAPI_BASE` variable
   - Update it to: `https://fire-detection-api.onrender.com` (your actual URL)
   - Save changes (service will restart)

### Step 5: Test Your Deployment

1. **Test FastAPI Service**
   ```bash
   curl https://fire-detection-api.onrender.com/detect/status
   ```
   Should return JSON with model status

2. **Test Flask Dashboard**
   - Visit: `https://fire-detection-dashboard.onrender.com`
   - You should see the dashboard
   - Try uploading an image
   - Check if alerts are created

## 🔧 Troubleshooting

### Build Fails
- **Check logs**: Look for specific error messages
- **Python version**: Render uses Python 3.9+ by default
- **Dependencies**: Verify all packages in requirements.txt are correct

### Model Not Found
- Verify `weights/best_swapped.pt` exists in repository
- Check `MODEL_PATH` environment variable
- Model will fallback to `yolov8n.pt` if custom model not found

### Services Can't Communicate
- Verify `FASTAPI_BASE` is set correctly in Flask service
- Check that FastAPI service is running
- Ensure CORS is configured (`ALLOW_ORIGINS: *`)

### Service Spins Down (Free Tier)
- Free tier services spin down after 15 min inactivity
- First request after spin-down takes 30-60 seconds
- Consider upgrading to Starter plan ($7/month) for always-on

## 📊 Service URLs

After deployment, you'll have:
- **FastAPI API**: `https://fire-detection-api.onrender.com`
- **Flask Dashboard**: `https://fire-detection-dashboard.onrender.com`

## 🎯 Next Steps After Deployment

1. **Test Image Upload**: Upload a test image through the dashboard
2. **Monitor Logs**: Check Render logs for any runtime errors
3. **Set Up Custom Domain** (optional): Configure in Render dashboard
4. **Upgrade Plan** (optional): For production use, consider Starter plan

## 💡 Tips

- **Free Tier**: Services are free but spin down after inactivity
- **Starter Plan**: $7/month per service - services stay awake
- **Database**: Currently using SQLite (ephemeral on free tier)
  - Consider PostgreSQL for production (Render offers free PostgreSQL)

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Check service logs in Render dashboard for specific errors
