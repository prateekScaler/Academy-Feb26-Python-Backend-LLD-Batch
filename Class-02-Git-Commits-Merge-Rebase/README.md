# Class 2: Git, Commits, Merge, Rebase

Restaurant Analogy: **How do multiple chefs work on the same recipe book?**

## Core Concepts

### Why Version Control?

| Approach | Problem |
|----------|---------|
| `report_FINAL_v2_ACTUALLY_FINAL.docx` | No meaningful history |
| Google Docs | No branching, no offline, auto-merges everything |
| Ctrl+Z | Lost when you close the app |
| **Git** | ✅ Meaningful checkpoints, branching, full history, works offline |

### Git Mental Model

| Concept | What it is | Restaurant Analogy |
|---------|------------|-------------------|
| Repository | Project folder + `.git` history | The recipe book |
| Commit | Snapshot with a message | "Added pasta recipe on page 42" |
| Branch | Parallel timeline | Chef experimenting with fusion dishes |
| HEAD | "You are here" pointer | Bookmark in the recipe book |

### The Three Areas

```
Working Directory  →  Staging Area  →  Repository
    (modified)         (git add)      (git commit)
```

### Commits = Linked List

Each commit stores:
- Snapshot of files
- Commit message
- **Parent pointer** (previous commit's hash)

```
[a1b2c3] ← [d4e5f6] ← [g7h8i9] ← [j0k1l2] ← HEAD
```

---

## Essential Commands

```bash
# Initialize
git init

# Check status
git status

# Stage changes
git add filename.py          # Specific file
git add .                    # All changes

# Commit
git commit -m "Add user login feature"

# View history
git log --oneline
git log --oneline --graph    # Visual branches

# Create branch
git branch feature/cart

# Switch branch
git checkout feature/cart
git switch feature/cart      # Modern (Git 2.23+)

# Create + switch
git checkout -b feature/cart
git switch -c feature/cart

# See differences
git diff                     # Unstaged changes
git diff --staged            # Staged changes
```

---

## Merge vs Rebase

### Merge
Creates a **new commit** with two parents. Preserves history.

```bash
git checkout main
git merge feature
```

**Use when:**
- Combining feature into main
- Commits are already pushed/shared
- You want to preserve "when integration happened"

### Rebase
**Replays** your commits on top of another branch. Linear history.

```bash
git checkout feature
git rebase main
```

**Use when:**
- Updating local feature branch with latest main
- Cleaning up before pushing
- Commits are NOT yet shared

### Golden Rule

> **Never rebase commits that have been pushed to a shared repository.**

---

## Why Merge Creates a New Commit

A merge commit:
1. Has **two parents** (both branches' last commits)
2. Records "these branches were integrated here"
3. Makes it easy to revert the entire merge
4. Preserves that work happened in parallel

---

## Commit Message Best Practices

```bash
# Bad
git commit -m "fix"
git commit -m "wip"
git commit -m "update"

# Good
git commit -m "feat: Add shopping cart functionality"
git commit -m "fix: Resolve payment timeout on slow connections"
git commit -m "refactor: Extract validation to separate module"
```

**Format:** `[type]: [what changed]`

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

---

## Demo Commands (For Instructor)

### Setup Demo Repo
```bash
mkdir git-demo && cd git-demo
git init
echo "# My Project" > README.md
git add README.md
git commit -m "Initial commit"
```

### Demonstrate Branching
```bash
# Create and switch to feature branch
git checkout -b feature/login

# Make changes
echo "def login(): pass" > auth.py
git add auth.py
git commit -m "feat: Add login function skeleton"

echo "def logout(): pass" >> auth.py
git add auth.py
git commit -m "feat: Add logout function"

# Show branches
git log --oneline --graph --all
```

### Demonstrate Merge
```bash
git checkout main
git merge feature/login
git log --oneline --graph
```

### Demonstrate Merge Conflict
```bash
# Setup conflict
git checkout main
echo "Main branch content" > conflict.txt
git add conflict.txt
git commit -m "Add conflict file on main"

git checkout -b feature/conflict
echo "Feature branch content" > conflict.txt
git add conflict.txt
git commit -m "Add conflict file on feature"

git checkout main
echo "Different main content" > conflict.txt
git add conflict.txt
git commit -m "Modify conflict file on main"

# Now merge - will conflict!
git merge feature/conflict

# Show conflict markers, resolve, commit
```

### Demonstrate Rebase
```bash
git checkout -b feature/rebase-demo
echo "Feature work" > feature.txt
git add feature.txt
git commit -m "Add feature work"

git checkout main
echo "Main work" > main.txt
git add main.txt
git commit -m "Add main work"

git checkout feature/rebase-demo
git rebase main
git log --oneline --graph
```

---

## Interactive Resources

| Resource | Type | Best For |
|----------|------|----------|
| [Learn Git Branching](https://learngitbranching.js.org/) | Interactive Tutorial | Understanding branching visually |
| [Oh My Git!](https://ohmygit.org/) | Game | Learning through play |
| [Git Exercises](https://gitexercises.fracz.com/) | Practice | Real scenario practice |
| [Oh Shit, Git!](https://ohshitgit.com/) | Reference | When things go wrong |

---

## Assignment

1. Create a new folder and initialize Git
2. Create a file, stage, and commit
3. Create a feature branch
4. Make commits on feature branch
5. Switch to main, make different changes
6. Try merging (resolve any conflicts)
7. View history with `git log --oneline --graph`

**Next class:** Push to GitHub, create Pull Requests!

---

## Interview Questions

1. **What is Git and why do we use it?**
   > Distributed VCS for tracking changes, collaboration, branching, and history.

2. **Difference between git add and git commit?**
   > `add` stages changes, `commit` saves them permanently with a message.

3. **When to use merge vs rebase?**
   > Merge for shared branches, rebase for local cleanup before pushing.

4. **What is HEAD?**
   > Pointer to current commit. "You are here" marker.

5. **Why does merge create a new commit?**
   > Records integration point with two parents, easy to revert, preserves parallel history.
