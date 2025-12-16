# Deployment Guide

This guide covers deploying AsesorAIrrechisimo to Streamlit Cloud and other platforms.

## Prerequisites

- GitHub account
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Python 3.8+ for local testing

## Deploying to Streamlit Cloud (Recommended)

Streamlit Cloud provides free hosting for Streamlit applications.

### 1. Push to GitHub

Ensure your code is pushed to a GitHub repository:

```bash
git add .
git commit -m "Ready for deployment"
git push origin refactor
```

### 2. Sign up for Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Authorize Streamlit to access your repositories

### 3. Deploy Your App

1. Click "New app"
2. Select your repository: `AsesorAIrrechisimo`
3. Choose branch: `refactor` (or `master` after merging)
4. Main file path: `portfolio_manager.py`
5. Click "Deploy"

### 4. Configuration

Streamlit Cloud will automatically:
- Install dependencies from `requirements.txt`
- Use Python 3.11 (configurable)
- Provide HTTPS and a subdomain URL

### 5. Environment Variables (Optional)

While the app accepts API keys through the UI, you can optionally set environment variables in Streamlit Cloud:

1. Go to app settings (⚙️ icon)
2. Click "Secrets"
3. Add (if desired for default values):
   ```toml
   # Not recommended - users should enter their own keys
   # ANTHROPIC_API_KEY = "sk-ant-..."
   ```

**Note:** It's recommended to have users enter their own API keys through the sidebar for security and cost management.

## Alternative Deployment Options

### Heroku

1. Create `Procfile`:
   ```
   web: streamlit run portfolio_manager.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   \n\
   " > ~/.streamlit/config.toml
   ```

3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku refactor:master
   ```

### Docker

1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8501

   CMD ["streamlit", "run", "portfolio_manager.py"]
   ```

2. Build and run:
   ```bash
   docker build -t asesor-airrecho .
   docker run -p 8501:8501 asesor-airrecho
   ```

### AWS EC2

1. Launch an EC2 instance (Ubuntu recommended)
2. SSH into the instance
3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   git clone https://github.com/yourusername/AsesorAIrrechisimo.git
   cd AsesorAIrrechisimo
   pip3 install -r requirements.txt
   ```

4. Run with nohup:
   ```bash
   nohup streamlit run portfolio_manager.py --server.port 8501 &
   ```

5. Configure security group to allow port 8501

## Production Considerations

### Security

1. **API Keys**: Never commit API keys to the repository
2. **HTTPS**: Streamlit Cloud provides HTTPS automatically
3. **Input Validation**: Already implemented in refactored version
4. **Rate Limiting**: Consider implementing for public deployments

### Performance

1. **Caching**: Streamlit's `@st.cache_data` is used where appropriate
2. **Session State**: Efficiently manages user data
3. **API Calls**: Optimized to minimize Claude API usage

### Monitoring

1. **Streamlit Cloud Logs**: Access logs through the Streamlit Cloud dashboard
2. **Error Tracking**: Application logging is configured
3. **Usage Metrics**: Monitor API usage through Anthropic console

### Cost Management

1. **API Costs**: Users bring their own API keys
2. **Hosting**: Streamlit Cloud free tier includes:
   - 1 GB RAM
   - 1 CPU
   - Unlimited apps (public)

## Configuration Files

### `.streamlit/config.toml` (Optional)

Create this file for custom Streamlit configuration:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
```

### `.gitignore` Updates

Ensure these are in `.gitignore`:
```
.env
.streamlit/secrets.toml
__pycache__/
*.pyc
.pytest_cache/
htmlcov/
.coverage
```

## Testing Before Deployment

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run application locally
streamlit run portfolio_manager.py
```

### Verify Functionality

1. ✅ API key validation works
2. ✅ Portfolio CRUD operations
3. ✅ CSV import/export
4. ✅ Real-time pricing
5. ✅ Chat functionality
6. ✅ Quick analysis buttons
7. ✅ Error handling

## Troubleshooting

### Common Issues

**Issue: Module not found errors**
```bash
# Solution: Ensure you're in the project root
cd /path/to/AsesorAIrrechisimo
pip install -r requirements.txt
```

**Issue: API key errors**
```
Solution: Verify API key format starts with "sk-ant-"
```

**Issue: yfinance not fetching prices**
```
Solution: This is normal for some tickers. The app falls back to manual prices.
```

**Issue: Streamlit Cloud deployment fails**
```
Solution: Check requirements.txt has all dependencies with correct versions
```

### Logs

**Streamlit Cloud:**
- Access logs from the app dashboard
- Click "Manage app" → "Logs"

**Local:**
```bash
# Run with debug logging
LOG_LEVEL=DEBUG streamlit run portfolio_manager.py
```

## Updating Deployment

### Streamlit Cloud

Automatic deployment:
1. Push changes to GitHub
2. Streamlit Cloud auto-deploys from connected branch
3. App updates within ~2 minutes

Manual reboot:
1. Go to app dashboard
2. Click "Reboot app"

### Rolling Back

If issues occur:
```bash
git checkout previous-working-commit
git push origin refactor --force
```

## Post-Deployment Checklist

- [ ] App loads without errors
- [ ] API key input works
- [ ] Can add/edit/delete holdings
- [ ] CSV import/export functional
- [ ] Chat responds correctly
- [ ] Quick analysis buttons work
- [ ] Error messages display properly
- [ ] Mobile responsive (test on phone)

## Support

For deployment issues:
- **Streamlit**: [community.streamlit.io](https://community.streamlit.io)
- **GitHub Issues**: Report bugs in the repository
- **Anthropic API**: [support.anthropic.com](https://support.anthropic.com)

## Best Practices

1. **Version Control**: Always tag releases
   ```bash
   git tag -a v2.0 -m "Refactored release"
   git push origin v2.0
   ```

2. **Testing**: Run tests before deployment
   ```bash
   pytest --cov=src
   ```

3. **Documentation**: Keep README.md updated

4. **Monitoring**: Check logs regularly for errors

5. **User Feedback**: Monitor for common user issues

## Next Steps

After successful deployment:
1. Test all features thoroughly
2. Share URL with users
3. Monitor usage and errors
4. Collect user feedback
5. Plan future improvements
