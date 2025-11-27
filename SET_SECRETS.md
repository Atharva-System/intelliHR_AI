# Set GitHub Secrets from .env.stage

## Commands to Set Secrets

Run these commands from the repository directory to set GitHub secrets from `.env.stage`:

```bash
cd /home/pujanp/Pujan/Atharva/talent-pulse/talent-pulse-repo/intelliHR_AI

# Set ENV_FILE_CONTENT secret (for pp/main branch)
cat .env.stage | gh secret set ENV_FILE_CONTENT

# Set STAGE_ENV_FILE_CONTENT secret (for stage branch)
cat .env.stage | gh secret set STAGE_ENV_FILE_CONTENT
```

## Alternative: Specify Repository

If you need to specify the repository explicitly:

```bash
# Set ENV_FILE_CONTENT secret
cat .env.stage | gh secret set ENV_FILE_CONTENT --repo Atharva-System/intelliHR_AI

# Set STAGE_ENV_FILE_CONTENT secret
cat .env.stage | gh secret set STAGE_ENV_FILE_CONTENT --repo Atharva-System/intelliHR_AI
```

## Verify Secrets

To verify the secrets were set:

```bash
gh secret list
```

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- Repository admin access or write permissions to secrets
- `.env.stage` file exists in the repository directory

## Notes

- The secrets will contain the entire content of `.env.stage`
- Both secrets are set to the same content by default
- You can update them separately if needed for different environments

