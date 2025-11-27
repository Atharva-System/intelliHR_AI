# GitHub Secrets Setup for AI Service

## Required GitHub Secrets

The AI service workflow requires the following secrets to be configured in GitHub:

### How to Add Secrets

1. Go to your repository: `Atharva-System/intelliHR_AI`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below:

### Required Secrets

| Secret Name | Description | Required | Example |
|------------|-------------|----------|---------|
| `API_KEY_1` | First Gemini API key | ✅ Yes | `AIza...` |
| `API_KEY_2` | Second Gemini API key (for fallback) | ⚠️ Optional | `AIza...` |
| `API_KEY_3` | Third Gemini API key (for fallback) | ⚠️ Optional | `AIza...` |
| `MODEL` | Gemini model name | ⚠️ Optional | `gemini-2.0-flash` (default) |
| `LANGSMITH_API_KEY` | LangSmith API key for logging | ⚠️ Optional | `lsv2_...` |
| `LANGSMITH_PROJECT` | LangSmith project name | ⚠️ Optional | `intellihr-ai-staging` |
| `AWS_ROLE_ARN` | AWS IAM role ARN for OIDC | ✅ Yes | `arn:aws:iam::123456789012:role/GitHubActionsDeployRole` |

### Notes

- **API_KEY_1** is required. The service will use API_KEY_2 and API_KEY_3 as fallbacks if API_KEY_1 fails.
- **MODEL** defaults to `gemini-2.0-flash` if not provided.
- **LANGSMITH_API_KEY** and **LANGSMITH_PROJECT** are optional and only needed if you're using LangSmith for observability.
- **AWS_ROLE_ARN** is required for AWS authentication (ECR, ECS).

### Workflow Changes

The workflow now:
- ✅ Uses `docker/build-push-action@v5` plugin for building and pushing
- ✅ Uses `aws-actions/amazon-ecs-render-task-definition@v1` for task definition rendering
- ✅ Uses `aws-actions/amazon-ecs-deploy-task-definition@v1` for ECS deployment
- ✅ Passes secrets as Docker build arguments
- ✅ Includes Docker layer caching for faster builds

### Docker Build Process

The Dockerfile now:
- Accepts build arguments for all secrets
- Creates `.env` file from build args if provided
- Falls back to copying `.env.${ENVIRONMENT}` file if build args are not provided

This ensures secrets are baked into the Docker image at build time, not at runtime.

