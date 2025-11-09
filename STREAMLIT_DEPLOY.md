# 🚀 Deploy PONS Auto Dashboard to Streamlit Cloud

## Quick Deploy (5 minutes)

### Step 1: Go to Streamlit Cloud
Visit: https://share.streamlit.io

### Step 2: Sign In
- Click **"Sign in"** (top right)
- Choose **"Continue with GitHub"**
- Authorize Streamlit to access your repositories

### Step 3: Deploy New App
1. Click **"New app"** button
2. Fill in the deployment form:
   - **Repository**: `officialbrandonsandoval-source/pons-auto`
   - **Branch**: `main`
   - **Main file path**: `dashboard/app.py`
   - **App URL**: (leave as suggested or customize)

3. Click **"Advanced settings"** (optional but recommended):
   - **Python version**: `3.9`
   - **Secrets**: Add your API keys (see below)

4. Click **"Deploy!"**

### Step 4: Configure Secrets (Important!)

After deployment starts, click **"Advanced settings" > "Secrets"** and paste:

```toml
# Minimum required for demo mode
OPENAI_API_KEY = "your-openai-api-key-here"

# Optional: Connect to backend API (if deployed separately)
# API_BASE_URL = "https://your-backend-api.com/api/v1"

# Optional: Full features
DATABASE_URL = "sqlite:///./pons_auto.db"
SECRET_KEY = "your-secret-key-here"
STRIPE_SECRET_KEY = "sk_test_your_stripe_key"
STRIPE_PUBLISHABLE_KEY = "pk_test_your_stripe_key"
```

**Get OpenAI API Key**: https://platform.openai.com/api-keys

### Step 5: Wait for Deployment
- Initial deployment takes 2-3 minutes
- Watch the logs for any errors
- Once complete, your app will be live!

## Your Live URLs

After deployment completes:
- **Dashboard**: `https://officialbrandonsandoval-source-pons-auto.streamlit.app`
- **Logs/Settings**: Accessible from Streamlit Cloud dashboard

## Demo Mode vs Full Mode

### Demo Mode (No Backend Required)
The dashboard works standalone for:
- ✅ AI Description Generator
- ✅ Photo Manager & Cropper
- ✅ Description Library
- ✅ Vehicle Preview
- ⚠️ Publishing features will be disabled (need backend API)

### Full Mode (Backend Required)
To enable all features, deploy the FastAPI backend separately:

**Option A: Railway.app**
```bash
# In your terminal
railway login
railway init
railway up
```

**Option B: Render.com**
1. Go to https://render.com
2. Connect GitHub repository
3. Create new "Web Service"
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn pons.main:app --host 0.0.0.0 --port 10000`
6. Add environment variables from `.streamlit/secrets.toml.example`

Then update Streamlit secrets with:
```toml
API_BASE_URL = "https://your-backend-url.com/api/v1"
```

## Troubleshooting

### "ModuleNotFoundError"
- Make sure `dashboard/requirements.txt` is present
- Check Python version is 3.9+

### "Connection Error" when publishing
- This is normal in demo mode (no backend)
- Deploy backend API to enable full features

### "Invalid OpenAI API Key"
- Verify key in Secrets settings
- Get new key from https://platform.openai.com/api-keys

### App is slow
- Free tier has resource limits
- Consider Streamlit Cloud paid tier for production

## Custom Domain (Optional)

1. Go to Streamlit Cloud dashboard
2. Click your app > Settings > General
3. Add custom domain (requires DNS configuration)

## Monitoring & Logs

- View logs: Streamlit Cloud dashboard > Your app > Logs
- View analytics: Built into Streamlit Cloud
- Monitor usage: OpenAI dashboard for API usage

## Update Your Deployment

To push updates:
```bash
git add .
git commit -m "Update dashboard"
git push
```

Streamlit Cloud will auto-deploy changes from GitHub!

## Support

- Streamlit Docs: https://docs.streamlit.io
- Community Forum: https://discuss.streamlit.io
- PONS Auto Issues: https://github.com/officialbrandonsandoval-source/pons-auto/issues

---

**Next Steps After Deployment:**
1. ✅ Test all features on mobile and desktop
2. ✅ Share your live demo link
3. ✅ Update README with actual live URL
4. 🚀 Deploy backend for full functionality
