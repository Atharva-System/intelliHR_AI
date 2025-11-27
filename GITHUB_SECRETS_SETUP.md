# GitHub Secrets Setup for AI Service

## Required GitHub Secrets

The AI service workflow uses a **single secret** containing the entire `.env` file content. This is much simpler than managing individual environment variables!

### How to Add Secrets

1. Go to your repository: `Atharva-System/intelliHR_AI`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the secrets below:

### Required Secrets

| Secret Name | Description | Required | Example |
|------------|-------------|----------|---------|
| `ENV_FILE_CONTENT` | Complete `.env` file content for `pp/main` branch | ✅ Yes | See format below |
| `STAGE_ENV_FILE_CONTENT` | Complete `.env` file content for `stage` branch | ✅ Yes (if using stage branch) | See format below |
| `AWS_ROLE_ARN` | AWS IAM role ARN for OIDC | ✅ Yes | `arn:aws:iam::123456789012:role/GitHubActionsDeployRole` |

### ENV_FILE_CONTENT Format

The `ENV_FILE_CONTENT` secret should contain the **entire `.env` file content** as a single multi-line string. For example:

```
API_KEY_1=AIzaSy...
API_KEY_2=AIzaSy...
API_KEY_3=AIzaSy...
MODEL=gemini-2.0-flash
MAX_OUTPUT_TOKENS=10000
TEMPERATURE=0.2
SAVE_DIR=downloaded_files
MAX_FILE_SIZE=10485760
MAX_FILES_PER_REQUEST=10
MINIMUM_ELIGIBLE_SCORE=60
ALLOWED_FILE_TYPES=application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document
LOG_LEVEL=INFO
LOG_FILE=app.log
API_HOST=0.0.0.0
API_PORT=80
DEBUG_MODE=false
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=intellihr-ai-staging
```

### Branch-Based Secrets

- **`pp/main` branch**: Uses `ENV_FILE_CONTENT` secret
- **`stage` branch**: Uses `STAGE_ENV_FILE_CONTENT` secret
- **`AWS_ROLE_ARN`**: Shared across all branches

### How It Works

1. The workflow creates a `.env` file directly from the GitHub secret (`ENV_FILE_CONTENT` or `STAGE_ENV_FILE_CONTENT`) based on the branch
2. The Dockerfile simply copies `.env` to `.env` during build
3. No need to manage individual environment variables - just paste your entire `.env` file content into the secret!

### Workflow Features

- ✅ Uses `docker/build-push-action@v5` plugin for building and pushing
- ✅ Uses `aws-actions/amazon-ecs-render-task-definition@v1` for task definition rendering
- ✅ Uses `aws-actions/amazon-ecs-deploy-task-definition@v1` for ECS deployment
- ✅ Includes Docker layer caching for faster builds
- ✅ Supports branch-based secrets (different `.env` content for different branches)

### Docker Build Process

The workflow:
- ✅ Creates `.env` file directly from GitHub secrets before building
- ✅ Uses branch-based secrets (different content for different branches)
  - `pp/main` branch: uses `ENV_FILE_CONTENT` secret
  - `stage` branch: uses `STAGE_ENV_FILE_CONTENT` secret

The Dockerfile:
- ✅ Simply copies `.env` to `.env` during build
- ✅ No build arguments needed

This ensures:
- Secrets are baked into the Docker image at build time
- No `.env` files are committed to the repository
- Simple management - just one secret with all environment variables
- The `.env` file is created dynamically from secrets in the workflow
