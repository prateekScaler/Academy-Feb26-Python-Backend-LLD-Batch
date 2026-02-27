# Class 3: Git Remotes, Forks, PRs & Merge Conflicts

Restaurant Analogy: **Your restaurant is now a franchise! How do multiple locations share recipes without chaos?**

---

## Revision: Class 2 Quick Quiz

### Q1: What makes a merge commit special?
> It has **TWO parents** — pointing to both branch tips. This preserves the complete history of parallel development.

### Q2: Rebase Direction — You want to update your `feature` branch with latest `main`. Which commands?
> `git checkout feature` then `git rebase main`
>
> **Memory trick:** "I sit on the throne" — checkout the branch you want to MOVE, rebase onto the branch you want to SIT ON.
>
> ❌ NEVER do `git checkout main && git rebase feature` — this rewrites main!

### Q3: Which statements about rebase are TRUE?
> **A) TRUE:** Rebase creates new commits with different SHA hashes
> **B) FALSE:** Original commits are orphaned, not preserved
> **C) TRUE:** Rebase results in linear history (no merge commits)
> **D) FALSE:** Never rebase pushed commits!

### Q4: When is rebase appropriate?
> Updating your LOCAL feature branch with latest main before creating a PR.
>
> **Rule:** Rebase YOUR private branch onto the shared branch. Never the other way around.

### Q5: What's a good commit message?
> `fix: Resolve login button tap area on mobile`
> - Prefixed with type (fix, feat, refactor)
> - Concise (50-72 chars)
> - Descriptive of WHAT and WHY

### Q6: After `git add`, where is your change?
> **Staging Area** — ready to commit but not yet saved permanently.

### Q7: Best practice for feature development?
> Create feature branch → atomic commits → clear messages → PR with code review → merge to main

---

## Git Remotes

A **remote** is a copy of your repository hosted elsewhere (GitHub, GitLab, etc.).

### Key Commands

```bash
# View remotes
git remote -v

# Add a remote
git remote add origin https://github.com/you/repo.git

# Push to remote
git push origin main

# Pull from remote (fetch + merge)
git pull origin main

# Fetch without merging (safe peek)
git fetch origin
```

### Push vs Pull vs Fetch

| Command | What it does |
|---------|--------------|
| `git push` | Upload your commits to remote |
| `git pull` | Download AND merge remote changes (fetch + merge) |
| `git fetch` | Download changes without merging |

### Remote Tracking Branches (Read-Only vs Local)

When you clone, Git creates **two types of branches**:

| Type | Example | Can Commit? | Purpose |
|------|---------|-------------|---------|
| **Local branches** | `main`, `feature/login` | ✅ Yes | Your working copies |
| **Remote tracking** | `origin/main`, `origin/feature` | ❌ No | Bookmarks showing where remote was |

```bash
# See all branches (local + remote tracking)
git branch -a
```

### Fetch vs Pull: The Real Difference

**`git fetch`:**
1. Downloads new commits from remote
2. Updates `origin/main` (tracking branch)
3. Does NOT touch your local `main`
4. Safe — you can review before merging

**`git pull`:**
1. Runs `git fetch` first
2. Then runs `git merge origin/main`
3. Modifies your local `main`
4. May cause merge conflicts

**When to use:**
- Use `fetch` when you want to see changes first: `git diff main origin/main`
- Use `pull` when you trust remote and want to quickly sync

### git push -u (Set Upstream Tracking)

```bash
# First push of a new branch - sets up tracking
git push -u origin feature/my-branch

# After -u is set, these work without specifying remote:
git push    # knows to push to origin/feature/my-branch
git pull    # knows to pull from origin/feature/my-branch
```

**What `-u` does:** Creates a link between local branch and remote branch so Git remembers where to push/pull.

### "origin" vs "upstream"

- **origin** — Your fork or primary remote (default name after clone)
- **upstream** — The original repo you forked from

---

## Forking

A **fork** is your personal GitHub copy of someone else's repository.

### Fork vs Clone

| Action | What happens |
|--------|--------------|
| **Clone** | Downloads repo to your computer |
| **Fork** | Creates YOUR copy on GitHub, then you clone that |

### When to Fork

- ✅ Contributing to open source (you don't have push access)
- ✅ Experimenting without affecting original
- ❌ Not needed if you're a collaborator with push access

### Fork Workflow

```bash
# 1. Fork on GitHub (click "Fork" button)

# 2. Clone YOUR fork
git clone https://github.com/YOU/repo.git

# 3. Add upstream (original repo)
git remote add upstream https://github.com/ORIGINAL/repo.git

# 4. Create branch, make changes, commit

# 5. Push to YOUR fork
git push origin your-branch

# 6. Create Pull Request (your fork → original)
```

### Keeping Fork Updated

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

---

## Pull Requests (PRs)

A **Pull Request** is a proposal to merge your changes. It's where code review happens.

> "Hey, I made changes on my branch. Can you **pull** them into main?"

### PR Lifecycle

1. **Create branch** — Work on feature locally
2. **Push to remote** — `git push origin feature/branch`
3. **Open PR** — On GitHub, write description
4. **Code review** — Teammates review, comment
5. **Merge** — Once approved, merge to main

### Good PR Practices

**Do:**
- Write clear title describing the change
- Explain WHY, not just WHAT
- Keep PRs small and focused
- Add screenshots for UI changes
- Link related issues

**Don't:**
- Create huge PRs (50+ files)
- Leave description empty
- Mix unrelated changes
- Ignore reviewer comments

### PR Description Template

```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
- [x] Unit tests pass
- [x] Manual testing done

## Related Issues
Closes #42
```

---

## Complete Workflows

### Team Workflow (Same Repo)

```bash
git checkout -b feature/my-feature
# Make changes, commit
git push origin feature/my-feature
# Create PR on GitHub, get review, merge
git checkout main && git pull
```

### Open Source Workflow (Fork)

```bash
# Fork on GitHub
git clone https://github.com/YOU/repo.git
git remote add upstream https://github.com/ORIGINAL/repo.git
git checkout -b feature/contribution
# Make changes, commit
git push origin feature/contribution
# Create PR: your fork → original repo
```

---

## Quick Reference

| I want to... | Command |
|--------------|---------|
| See my remotes | `git remote -v` |
| Add a remote | `git remote add [name] [url]` |
| Push my branch | `git push origin [branch]` |
| Get latest changes | `git pull origin main` |
| Sync fork with upstream | `git fetch upstream && git merge upstream/main` |
| Create PR (CLI) | `gh pr create` |

---

## Assignment

1. Fork a classmate's repository
2. Clone your fork locally
3. Add upstream remote
4. Create a feature branch
5. Make a small change, commit with good message
6. Push to your fork
7. Create a Pull Request to the original repo
8. Review someone else's PR, leave a comment

---

## Merge Conflicts

A **conflict** occurs when Git can't automatically merge because the same lines were changed differently in both branches.

### What a Conflict Looks Like

```
<<<<<<< HEAD
price = 99  # Your current branch
=======
price = 149  # Incoming branch
>>>>>>> feature/new-pricing
```

### How to Resolve

1. Git tells you there's a conflict
2. Open the file, find conflict markers
3. Decide what to keep (yours, theirs, both, or something new)
4. Remove ALL conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
5. Stage and commit: `git add file.py && git commit -m "fix: Resolve conflict"`

### Abort a Merge

```bash
# If you want to cancel and start over
git merge --abort
```

---

## Optional: More Git Tools

### git stash — Temporarily Save Work

```bash
git stash              # Save uncommitted changes
git stash pop          # Restore saved changes
git stash list         # See all stashes
```

### .gitignore — Files to Never Track

```
# Common .gitignore entries
.env
node_modules/
__pycache__/
venv/
.DS_Store
*.log
```

### git reset — Understanding the Command

**Breaking down `git reset --hard HEAD~1`:**
- `git reset` — Move HEAD to a different commit
- `--hard` — Reset mode (how much to undo)
- `HEAD~1` — Where to go (1 commit back)

**The Three Modes:**

| Mode | Repository | Staging | Working Dir | Use Case |
|------|------------|---------|-------------|----------|
| `--soft` | ✅ Reset | ❌ Keep | ❌ Keep | Undo commit, keep changes staged |
| `--mixed` (default) | ✅ Reset | ✅ Reset | ❌ Keep | Undo commit, unstage, keep files |
| `--hard` ⚠️ | ✅ Reset | ✅ Reset | ✅ Reset | Nuclear - discard everything |

**Different ways to specify target:**

```bash
# Relative to HEAD
git reset --hard HEAD~1     # 1 commit back
git reset --hard HEAD~3     # 3 commits back

# Specific commit SHA
git reset --hard a1b2c3d    # Reset to this commit

# Branch name
git reset --hard origin/main  # Match remote exactly

# Using ^ (parent)
git reset --hard HEAD^      # Same as HEAD~1
```

**Common use cases:**

```bash
# "Oops, committed too early"
git reset --soft HEAD~1     # Undo commit, keep staged

# "Reorganize my commits"
git reset HEAD~3            # Undo 3 commits, keep files

# "Throw away all local changes"
git reset --hard origin/main  # Match remote exactly

# "Unstage a file"
git reset HEAD file.txt     # Unstage specific file
```

### git revert — Safe undo for pushed commits

```bash
git revert abc1234          # Creates new commit that undoes abc1234
git revert --no-commit abc  # Revert without auto-commit
```

| Command | Effect | Safe for pushed? |
|---------|--------|------------------|
| `git reset` | Removes commits, rewrites history | ❌ No |
| `git revert` | New commit that undoes changes | ✅ Yes |

**Rule:** Use `revert` for pushed commits, `reset` only for local unpushed work.

### HEAD~1 vs HEAD@{1} — Common Confusion!

These look similar but are **completely different**:

| Syntax | Meaning | Navigates |
|--------|---------|-----------|
| `HEAD~1` | Parent commit (1 back in history) | **Commit graph** (ancestry) |
| `HEAD@{1}` | Where HEAD was 1 operation ago | **Reflog** (time/actions) |

**Example:**
```
You're on commit D, then run: git checkout feature
Now HEAD points to commit X (tip of feature)

HEAD~1  = parent of X (commit on feature branch)
HEAD@{1} = commit D (where you WERE before checkout)
```

Quick reference:
- `HEAD~n` — Go back n commits in the tree
- `HEAD^n` — Select nth parent (for merge commits: ^1 = main, ^2 = merged branch)
- `HEAD@{n}` — Where HEAD was n operations ago (reflog)

### git commit --amend — Fix the last commit

```bash
# Fix commit message only
git commit --amend -m "New corrected message"

# Add forgotten files, keep same message
git add forgotten-file.txt
git commit --amend --no-edit

# Add files AND change message
git add extra-file.txt
git commit --amend -m "feat: Complete feature"

# Open editor to modify message
git commit --amend
```

⚠️ **Warning:** `--amend` rewrites history. Don't amend pushed commits unless you're the only one on the branch!

### git reflog — Your Git Time Machine

**What is reflog?** `reflog` = **ref**erence **log** — a diary of everywhere HEAD has pointed.

Every time you `commit`, `checkout`, `reset`, `merge`, or `rebase`, Git records the move.

```bash
$ git reflog
a1b2c3d HEAD@{0}: commit: Add payment feature
e4f5g6h HEAD@{1}: checkout: moving from main to feature
i7j8k9l HEAD@{2}: reset: moving to HEAD~3      # <- Oops!
m0n1o2p HEAD@{3}: commit: Fix critical bug     # <- This is "lost"
```

**Reading the output:**
- `a1b2c3d` — Commit SHA (first 7 chars)
- `HEAD@{0}` — Position (0 = current, 1 = previous, etc.)
- `commit: ...` — What action happened

**Recovery scenarios:**

```bash
# "I ran git reset --hard and lost commits!"
git reflog                     # Find the SHA before the reset
git reset --hard m0n1o2p       # Go back to it

# "I deleted a branch with unmerged work!"
git reflog | grep "feature"    # Find last commit on that branch
git checkout -b feature/recovered abc1234  # Recreate it
```

**Why does this work?** Git doesn't delete commits immediately. They become "unreachable" but exist for ~30 days until garbage collection.

### git cherry-pick — Copy One Commit

```bash
git cherry-pick abc123        # Copy commit to current branch
```

### git tag — Mark Releases

```bash
git tag v1.0.0                        # Create tag
git tag -a v1.0.0 -m "First release"  # Annotated tag
git push origin --tags                # Push tags to remote
```

---

## Practice Resources

### Interactive Learning

| Resource | Type | Best For |
|----------|------|----------|
| [Learn Git Branching](https://learngitbranching.js.org/) | Interactive Tutorial | Understanding branching visually |
| [Oh My Git!](https://ohmygit.org/) | Game | Learning through play |
| [GitMastery](https://www.gitmastery.me/) | Challenges | Progress through levels |
| [Git Exercises](https://gitexercises.fracz.com/) | Practice | Real scenario practice |
| [Oh Shit, Git!](https://ohshitgit.com/) | Reference | When things go wrong |

### Git Exercises to Complete

After this class, try exercises 5-8:
- **5. merge-conflict** — Resolve merge conflicts
- **6. save-your-work** — Git stash basics
- **7. change-branch-history** — Rebase practice
- **8. remove-ignored** — Working with .gitignore

---

## Assignment: Your First Open Source PR!

**Goal:** Add yourself to the contributors list by creating a Pull Request.

**Repository:** https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch

### Steps

1. **Fork** the repository on GitHub
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Academy-Feb26-Python-Backend-LLD-Batch.git
   cd Academy-Feb26-Python-Backend-LLD-Batch
   ```
3. **Add upstream** remote:
   ```bash
   git remote add upstream https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch.git
   ```
4. **Create branch**:
   ```bash
   git checkout -b add-student/your-name
   ```
5. **Edit** `CONTRIBUTORS.md` — Add your row to the table
6. **Commit**:
   ```bash
   git add CONTRIBUTORS.md
   git commit -m "feat: Add [Your Name] to contributors list"
   ```
7. **Push** to your fork:
   ```bash
   git push origin add-student/your-name
   ```
8. **Create PR** on GitHub — Click "Compare & pull request"

### Bonus Challenges

- Review a classmate's PR and leave a comment
- If you get a merge conflict, resolve it!
- After your PR is merged, sync your fork with upstream

---

## Interview Questions

1. **What is a remote in Git?**
   > A remote is a copy of the repository hosted elsewhere (like GitHub). It allows collaboration by syncing changes between local and remote.

2. **What's the difference between fork and clone?**
   > Clone downloads a repo to your computer. Fork creates your own copy on GitHub (server-side), which you then clone.

3. **What is a Pull Request?**
   > A PR is a proposal to merge changes from one branch to another. It enables code review before integration.

4. **When would you use `git fetch` instead of `git pull`?**
   > When you want to see what changed on remote without immediately merging. Fetch is safer — you can review before integrating.

5. **How do you keep a fork synchronized with the original repo?**
   > Add upstream remote, fetch from it, merge upstream/main into your main, push to origin.

6. **How do you resolve a merge conflict?**
   > Open the conflicted file, find conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`), decide what code to keep, remove the markers, then `git add` and `git commit` the resolution.

7. **What's the difference between `git reset` and `git revert`?**
   > `reset` rewrites history by removing commits (only for local unpushed work). `revert` creates a new commit that undoes changes (safe for pushed commits).

8. **What is `git stash` used for?**
   > Temporarily saves uncommitted changes so you can switch branches or do other work. Restore with `git stash pop`.
