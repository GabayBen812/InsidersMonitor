# Fixing Exposed Discord Bot Token

## ⚠️ CRITICAL: Revoke Your Token First!

Your Discord bot token was exposed in git history. **You MUST revoke it immediately:**

1. Go to: https://discord.com/developers/applications
2. Select your bot application
3. Go to **"Bot"** section
4. Click **"Reset Token"** or **"Regenerate Token"**
5. Copy the NEW token
6. Update your local `.env` file with the new token

## Clean Up Git History

After revoking the token, remove it from git history:

### Option 1: Interactive Rebase (Recommended)
```bash
# Start interactive rebase from before the bad commit
git rebase -i 5f2dd5d

# In the editor, change the commit 0cbe7c5 from "pick" to "edit"
# Save and close

# Remove .env from that commit
git rm --cached .env
git commit --amend --no-edit

# Continue rebase
git rebase --continue

# Force push (since we rewrote history)
git push --force-with-lease
```

### Option 2: Filter Branch (Removes from all commits)
```bash
# Remove .env from all commits in history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push --force-with-lease
```

### Option 3: BFG Repo-Cleaner (Easiest, but requires Java)
```bash
# Download BFG from: https://rtyley.github.io/bfg-repo-cleaner/
# Then run:
java -jar bfg.jar --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force-with-lease
```

## After Cleaning History

1. Verify `.env` is in `.gitignore` ✅ (already done)
2. Verify `.env` is not tracked: `git ls-files | grep .env` (should return nothing)
3. Update your local `.env` with the NEW token
4. Test the bot works with the new token
5. Push again

## Prevention

- ✅ `.env` is now in `.gitignore`
- ✅ Never commit `.env` files
- ✅ Use `.env.example` as a template
- ✅ Review `git status` before committing

