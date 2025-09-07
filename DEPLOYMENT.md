# Deployment Guide

## Frontend Changes Made

The frontend now automatically detects the environment and uses the appropriate API URL:
- **Development**: Uses `http://localhost:8000/api/upload-resume`
- **Production**: Uses `${window.location.protocol}//${window.location.hostname}/api/upload-resume`

## Backend Changes Made

1. **Dynamic CORS Configuration**: The backend now supports environment-based CORS origins
2. **Environment Variable Support**: You can set `ALLOWED_ORIGINS` environment variable

## Deployment Steps

### Option 1: Same Domain Deployment (Recommended)
If your frontend and backend are served from the same domain:

1. **Frontend**: Deploy your static files to your web server
2. **Backend**: Deploy your Flask app to serve both static files and API endpoints
3. **No additional configuration needed** - the frontend will automatically use the same domain

### Option 2: Different Domains
If your frontend and backend are on different domains:

1. **Set Environment Variable**:
   ```bash
   export ALLOWED_ORIGINS="https://your-frontend-domain.com,https://www.your-frontend-domain.com"
   ```

2. **Update Frontend API URL** (if needed):
   ```javascript
   // In script.js, modify the getApiUrl function to use your backend domain
   const getApiUrl = () => {
       if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
           return 'https://your-backend-domain.com/api/upload-resume';
       } else {
           return 'http://localhost:8000/api/upload-resume';
       }
   };
   ```

## Testing Deployment

1. **Check API Health**: Visit `https://your-domain.com/api/health`
2. **Check Frontend**: Open browser console and look for API connectivity logs
3. **Test Upload**: Try uploading a resume to ensure the API connection works

## Common Issues

### ERR_CONNECTION_REFUSED
- **Cause**: Frontend trying to connect to localhost in production
- **Solution**: The updated code now automatically detects the environment

### CORS Errors
- **Cause**: Backend not allowing requests from your frontend domain
- **Solution**: Set the `ALLOWED_ORIGINS` environment variable with your frontend domain

### 404 Errors on API Endpoints
- **Cause**: Backend not properly configured to serve API routes
- **Solution**: Ensure your Flask app is properly deployed and serving the `/api/*` routes

## Environment Variables

```bash
# Optional: Set allowed CORS origins
ALLOWED_ORIGINS="https://your-frontend-domain.com,https://www.your-frontend-domain.com"

# Optional: Set Flask environment
FLASK_ENV=production
```

## Verification

After deployment, check:
1. ✅ Frontend loads without errors
2. ✅ API health endpoint responds: `/api/health`
3. ✅ Resume upload works end-to-end
4. ✅ No CORS errors in browser console
5. ✅ No ERR_CONNECTION_REFUSED errors
