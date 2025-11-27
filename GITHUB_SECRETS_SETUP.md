# GitHub Secrets Setup for AI Service

## Required GitHub Secrets

The AI service workflow requires the following secrets to be configured in GitHub. **All environment variables are passed as Docker build arguments** - there is no fallback to copying `.env` files.

### How to Add Secrets

1. Go to your repository: `Atharva-System/intelliHR_AI`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below:

### Branch-Based Secrets

The workflow supports **branch-based secrets**:
- **`stage` branch**: Uses secrets prefixed with `STAGE_*` (e.g., `STAGE_API_KEY_1`, `STAGE_MODEL`)
- **`pp/main` branch**: Uses default secrets (e.g., `API_KEY_1`, `MODEL`)

### Required Secrets

#### For `pp/main` branch (default):
| Secret Name | Description | Required | Example |
|------------|-------------|----------|---------|
| `API_KEY_1` | First Gemini API key | ✅ Yes | `AIza...` |
| `API_KEY_2` | Second Gemini API key (for fallback) | ⚠️ Optional | `AIza...` |
| `API_KEY_3` | Third Gemini API key (for fallback) | ⚠️ Optional | `AIza...` |
| `MODEL` | Gemini model name | ⚠️ Optional | `gemini-2.0-flash` |
| `MAX_OUTPUT_TOKENS` | Maximum output tokens | ⚠️ Optional | `10000` |
| `TEMPERATURE` | Model temperature | ⚠️ Optional | `0.2` |
| `SAVE_DIR` | Directory for saved files | ⚠️ Optional | `downloaded_files` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | ⚠️ Optional | `10485760` |
| `MAX_FILES_PER_REQUEST` | Max files per request | ⚠️ Optional | `10` |
| `MINIMUM_ELIGIBLE_SCORE` | Minimum eligible score | ⚠️ Optional | `60` |
| `ALLOWED_FILE_TYPES` | Allowed file MIME types | ⚠️ Optional | `application/pdf,...` |
| `LOG_LEVEL` | Logging level | ⚠️ Optional | `INFO` |
| `LOG_FILE` | Log file name | ⚠️ Optional | `app.log` |
| `API_HOST` | API host | ⚠️ Optional | `0.0.0.0` |
| `API_PORT` | API port | ⚠️ Optional | `80` |
| `DEBUG_MODE` | Debug mode | ⚠️ Optional | `false` |
| `LANGSMITH_API_KEY` | LangSmith API key | ⚠️ Optional | `lsv2_...` |
| `LANGSMITH_PROJECT` | LangSmith project name | ⚠️ Optional | `intellihr-ai-staging` |
| `AWS_ROLE_ARN` | AWS IAM role ARN for OIDC | ✅ Yes | `arn:aws:iam::123456789012:role/GitHubActionsDeployRole` |

#### For `stage` branch:
Use the same secrets but prefixed with `STAGE_*`:
- `STAGE_API_KEY_1`, `STAGE_API_KEY_2`, `STAGE_API_KEY_3`
- `STAGE_MODEL`, `STAGE_MAX_OUTPUT_TOKENS`, `STAGE_TEMPERATURE`
- `STAGE_SAVE_DIR`, `STAGE_MAX_FILE_SIZE`, `STAGE_MAX_FILES_PER_REQUEST`
- `STAGE_MINIMUM_ELIGIBLE_SCORE`, `STAGE_ALLOWED_FILE_TYPES`
- `STAGE_LOG_LEVEL`, `STAGE_LOG_FILE`
- `STAGE_API_HOST`, `STAGE_API_PORT`, `STAGE_DEBUG_MODE`
- `STAGE_LANGSMITH_API_KEY`, `STAGE_LANGSMITH_PROJECT`
- `AWS_ROLE_ARN` (same for all branches)

### Notes

- **API_KEY_1** (or **STAGE_API_KEY_1** for stage branch) is required. The service will use API_KEY_2 and API_KEY_3 as fallbacks if API_KEY_1 fails.
- All other secrets are optional and will only be included in `.env` if provided.
- When pushing to `stage` branch, the workflow automatically uses `STAGE_*` prefixed secrets.
- **AWS_ROLE_ARN** is required for AWS authentication (ECR, ECS) and is shared across all branches.

### Workflow Changes

The workflow now:
- ✅ Uses `docker/build-push-action@v5` plugin for building and pushing
- ✅ Uses `aws-actions/amazon-ecs-render-task-definition@v1` for task definition rendering
- ✅ Uses `aws-actions/amazon-ecs-deploy-task-definition@v1` for ECS deployment
- ✅ Passes secrets as Docker build arguments
- ✅ Includes Docker layer caching for faster builds

### Docker Build Process

The Dockerfile:
- ✅ Accepts build arguments for **all environment variables**
- ✅ Creates `.env` file **only from build args** (no fallback to copying `.env` files)
- ✅ Only includes environment variables in `.env` if they are provided as build args

This ensures:
- Secrets are baked into the Docker image at build time, not at runtime
- No `.env` files are committed to the repository
- Complete control over which environment variables are included

