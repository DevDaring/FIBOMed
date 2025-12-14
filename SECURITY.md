# Security Configuration

## API Keys Management

### Files with Secrets (NOT committed to git)
- `cloudbuild.yaml` - Contains actual API keys for GCP Cloud Run deployment
- `secrets/.env` - Contains environment variables with API keys
- `secrets/speech_key.json` - Google Cloud Speech credentials

### Template Files (Safe to commit)
- `cloudbuild.yaml.template` - Template for cloudbuild.yaml with placeholder values

## Setup Instructions

### 1. Create your local cloudbuild.yaml
Copy the template and add your real API keys:
```bash
cp cloudbuild.yaml.template cloudbuild.yaml
# Edit cloudbuild.yaml and replace placeholder values with actual keys
```

### 2. Exposed Keys - IMPORTANT
The following keys were previously exposed in git and should be rotated:

**Google API Keys:**
- Old GEMINI_API_KEY: `AIzaSyB6aL5WIX8iyHACvFozh05UJW151WuV7vY` ❌ ROTATE
- Old GOOGLE_API_KEY: `AIzaSyByCt9oeyr7Pzc6zfYAuR31X6CTmKh3qak` ❌ ROTATE
- Old FIBO_PROD_API_KEY: `4e0a4d8a453845779c76e10d69f49447` ❌ ROTATE

**Action Required:**
1. Generate new API keys in Google Cloud Console
2. Update `cloudbuild.yaml` with new keys
3. Update `secrets/.env` with new keys
4. Delete/revoke the old exposed keys

### 3. Current Setup
Your cloudbuild.yaml is now:
- ✅ Added to `.gitignore`
- ✅ Removed from git tracking
- ✅ Updated with new GEMINI_API_KEY from .env

The file remains on your local system for deployment but won't be committed to git.

## Deployment

Deploy to Cloud Run using:
```bash
gcloud builds submit --config=cloudbuild.yaml
```

The cloudbuild.yaml contains the actual keys needed for Cloud Run environment variables.
