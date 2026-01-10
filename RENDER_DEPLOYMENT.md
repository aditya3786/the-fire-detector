# Render Deployment Guide

This guide will help you deploy the Fire Detection System to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your project pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. Your trained YOLO model file (`best_swapped.pt` or `best.pt`) in the `weights/` directory

## Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. **Push your code to Git**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Connect Repository to Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your Git repository
   - Render will automatically detect `render.yaml` and create both services

3. **Configure Environment Variables**
   - After services are created, you can update environment variables in the Render dashboard if needed
   - The `render.yaml` already includes default values

4. **Upload Model File**
   - Render doesn't support large file uploads directly
   - You have two options:
     a. **Option A**: Include the model in your Git repository (if under 100MB)
     b. **Option B**: Use Render's disk storage and upload via a script after deployment
     c. **Option C**: Store model in cloud storage (S3, etc.) and download on startup

### Option 2: Manual Service Creation

If you prefer to create services manually:

#### 1. Create FastAPI Service

- **Type**: Web Service
- **Name**: `fire-detection-api`
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd platform && python -m uvicorn fastapi_app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `MODEL_PATH`: `weights/best_swapped.pt`
  - `DEVICE`: `cpu`
  - `CONF_THRESHOLD`: `0.10`
  - `IMGSZ`: `512`
  - `ALERT_CONF_THRESHOLD`: `0.50`
  - `WARMUP`: `true`
  - `ALLOW_ORIGINS`: `*`

#### 2. Create Flask Dashboard Service

- **Type**: Web Service
- **Name**: `fire-detection-dashboard`
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd platform/backend && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 app:app`
- **Environment Variables**:
  - `SECRET_KEY`: Generate a random secret key
  - `SQLALCHEMY_DATABASE_URI`: `sqlite:///instance/alerts.db`
  - `FASTAPI_BASE`: Set this to your FastAPI service URL (e.g., `https://fire-detection-api.onrender.com`)

## Important Notes

### Model File Location

The model file must be in the `weights/` directory at the project root. If your model is large:

1. **For models < 100MB**: Commit to Git
2. **For larger models**: 
   - Use a startup script to download from cloud storage
   - Or use Render's persistent disk (paid plans)

### Database

The Flask service uses SQLite by default. For production:
- Consider upgrading to PostgreSQL (Render offers free PostgreSQL)
- Update `SQLALCHEMY_DATABASE_URI` to use PostgreSQL connection string

### Service Communication

The Flask dashboard needs to communicate with the FastAPI service. The `FASTAPI_BASE` environment variable should be set to the FastAPI service URL.

### Health Checks

- FastAPI health check: `/detect/status`
- Flask health check: `/api/health`

## Post-Deployment

1. **Test the Services**
   - Visit your Flask dashboard URL
   - Test image upload functionality
   - Check that alerts are being created

2. **Monitor Logs**
   - Check Render logs for any errors
   - Verify model loading on FastAPI service

3. **Update CORS (if needed)**
   - If you have a custom frontend domain, update `ALLOW_ORIGINS` in FastAPI service

## Troubleshooting

### Model Not Found
- Verify model file is in `weights/` directory
- Check `MODEL_PATH` environment variable
- Review build logs for file structure

### Services Can't Communicate
- Verify `FASTAPI_BASE` is set correctly in Flask service
- Check that FastAPI service is running
- Review network logs

### Build Failures
- Check Python version (3.9-3.11 recommended)
- Verify all dependencies in `requirements.txt`
- Review build logs for specific errors

### Database Issues
- Ensure `instance/` directory is writable
- For SQLite, data persists on disk (free tier has ephemeral storage)
- Consider PostgreSQL for production

## Scaling

- **Free Tier**: Services spin down after 15 minutes of inactivity
- **Starter Plan**: Services stay awake, better for production
- **Professional Plan**: Auto-scaling, better performance

## Support

For Render-specific issues, check:
- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
