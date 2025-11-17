# Render Deployment Guide

This guide explains how to deploy the MCP Tool Lister to Render.

## Prerequisites

- A [Render account](https://render.com/) (free tier available)
- Your code pushed to a GitHub repository

## Deployment Files

The following files are configured for Render deployment:

- **`render.yaml`**: Blueprint configuration for automated deployment
- **`Procfile`**: Process file specifying how to run the app
- **`runtime.txt`**: Specifies Python version (3.11.0)
- **`requirements.txt`**: Python dependencies including gunicorn

## Deployment Methods

### Method 1: Blueprint Deployment (Recommended)

This is the easiest method as Render will automatically configure everything.

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create New Blueprint on Render**
   - Go to https://dashboard.render.com/
   - Click "New" → "Blueprint"
   - Select your GitHub repository
   - Render detects `render.yaml` automatically
   - Click "Apply" to deploy

3. **Configure Environment Variables** (Optional)
   - After deployment, go to your service dashboard
   - Navigate to "Environment" tab
   - Add `OPENAI_API_KEY` if using AI features

### Method 2: Manual Web Service

If you prefer manual configuration:

1. **Push to GitHub** (same as above)

2. **Create New Web Service**
   - Go to https://dashboard.render.com/
   - Click "New" → "Web Service"
   - Connect your GitHub repository

3. **Configure Service**
   ```
   Name: mcp-tool-lister
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
   Plan: Free
   ```

4. **Add Environment Variables** (if needed)
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `OPENAI_MODEL`: gpt-4-turbo-preview (or your preferred model)

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | No | OpenAI API key for AI features | None |
| `OPENAI_MODEL` | No | OpenAI model to use | gpt-4-turbo-preview |
| `PORT` | Auto | Port number (set by Render) | Set by Render |

## Post-Deployment

### Access Your Application
Your app will be available at:
```
https://your-service-name.onrender.com
```

### Monitor Logs
- Go to your service dashboard on Render
- Click "Logs" to view application logs
- Monitor for any errors or issues

### Update Your Application
Any push to your GitHub repository will trigger automatic redeployment:
```bash
git add .
git commit -m "Update application"
git push origin main
```

## Important Notes

### Free Tier Limitations
- **Spin Down**: Services spin down after 15 minutes of inactivity
- **Cold Start**: First request after spin down takes 30-60 seconds
- **Monthly Limit**: 750 hours of runtime per month

### Production Considerations
- Upgrade to paid plan for:
  - No spin down
  - Faster builds
  - More resources
  - Custom domains

## Troubleshooting

### Build Fails
- Check `requirements.txt` for correct dependencies
- Verify Python version in `runtime.txt` is supported
- Check build logs for specific errors

### Application Won't Start
- Verify `Procfile` or start command is correct
- Check logs for Python errors
- Ensure `app.py` has proper Flask app definition

### MCP Server Connection Issues
- Note: Some MCP servers require Node.js/npm
- Render's Python environment may not have npm by default
- Consider using servers that don't require external dependencies

### Performance Issues
- Increase workers in gunicorn command (paid plan)
- Use caching for frequently accessed data
- Optimize MCP server connections

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Render Python Guide](https://render.com/docs/deploy-flask)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render Free Tier](https://render.com/docs/free)

## Support

For issues specific to:
- **Render Deployment**: Check [Render Community](https://community.render.com/)
- **Application Issues**: Open an issue on your GitHub repository
