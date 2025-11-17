# Render Deployment Checklist

Use this checklist to ensure smooth deployment to Render.

## Pre-Deployment Checklist

- [ ] All code is committed to Git
- [ ] Code is pushed to GitHub repository
- [ ] `requirements.txt` includes all dependencies
- [ ] `Procfile` is configured correctly
- [ ] `render.yaml` blueprint is present
- [ ] `runtime.txt` specifies Python version
- [ ] `.gitignore` excludes sensitive files (.env, __pycache__, etc.)
- [ ] Remove any hardcoded secrets or API keys from code

## Render Account Setup

- [ ] Created account at https://render.com
- [ ] Connected GitHub account to Render
- [ ] Verified email address

## Deployment Steps

### Using Blueprint (Recommended)
- [ ] Navigate to Render Dashboard
- [ ] Click "New" → "Blueprint"
- [ ] Select your GitHub repository
- [ ] Review detected configuration from render.yaml
- [ ] Click "Apply" to create service
- [ ] Wait for build to complete

### Using Manual Setup (Alternative)
- [ ] Navigate to Render Dashboard
- [ ] Click "New" → "Web Service"
- [ ] Select your GitHub repository
- [ ] Configure service settings:
  - [ ] Name: mcp-tool-lister
  - [ ] Runtime: Python 3
  - [ ] Build Command: pip install -r requirements.txt
  - [ ] Start Command: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
  - [ ] Plan: Free (or your choice)
- [ ] Click "Create Web Service"

## Post-Deployment

- [ ] Wait for initial build and deployment (3-5 minutes)
- [ ] Check deployment logs for errors
- [ ] Visit your application URL
- [ ] Test the web interface
- [ ] Test API endpoints
- [ ] Verify configuration loading works

## Optional Environment Variables

If using OpenAI features:
- [ ] Add OPENAI_API_KEY in Render Environment tab
- [ ] Add OPENAI_MODEL (optional)
- [ ] Redeploy to apply environment variables

## Verification

- [ ] Application loads successfully
- [ ] Static files (CSS, JS) are served correctly
- [ ] Configuration form accepts input
- [ ] Tool listing functionality works
- [ ] No console errors in browser

## Troubleshooting

If deployment fails:
- [ ] Check build logs in Render dashboard
- [ ] Verify all files are in repository
- [ ] Check Python version compatibility
- [ ] Review requirements.txt for issues
- [ ] Check Procfile syntax
- [ ] Verify app.py has correct Flask app object

## Production Ready

- [ ] Application is accessible via Render URL
- [ ] Core functionality tested
- [ ] Documentation updated with live URL
- [ ] (Optional) Custom domain configured
- [ ] (Optional) Upgraded to paid plan for better performance

## Notes

- Free tier spins down after 15 minutes of inactivity
- First request after spin down takes 30-60 seconds
- 750 hours/month limit on free tier
- Automatic redeployment on GitHub push

---

Last Updated: November 17, 2025
