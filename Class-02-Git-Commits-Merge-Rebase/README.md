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

### Starting Point (Both Examples)

```
          C1 ← C2 ← C3  (feature)
         /
A ← B ← D ← E  (main)
```

You created `feature` from `main` at commit `B`. Both branches have new commits since then.

---

### Merge
Creates a **new commit** with two parents. Preserves history.

```bash
git checkout main
git merge feature
```

**Before Merge:**
```
          C1 ← C2 ← C3  (feature)
         /
A ← B ← D ← E  (main) ← HEAD
```

**After Merge:**
```
          C1 ← C2 ← C3
         /            \
A ← B ← D ← E ←――――――― M  (main) ← HEAD
```

- `M` is a **merge commit** with two parents: `E` and `C3`
- History shows parallel work happened
- Easy to see when feature was integrated

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

**Before Rebase:**
```
          C1 ← C2 ← C3  (feature) ← HEAD
         /
A ← B ← D ← E  (main)
```

**After Rebase:**
```
A ← B ← D ← E  (main)
              \
               C1' ← C2' ← C3'  (feature) ← HEAD
```

- Original `C1, C2, C3` are **replayed** as new commits `C1', C2', C3'`
- The `'` indicates these are **new commits** (different hashes!)
- History looks linear – as if you started from `E`
- Old commits `C1, C2, C3` become orphaned (eventually garbage collected)

**Use when:**
- Updating local feature branch with latest main
- Cleaning up before pushing
- Commits are NOT yet shared

---

### ⚠️ Rebase Direction: Which Branch Do I Rebase?

This is the **#1 source of confusion** with rebase. Let's compare both scenarios:

**Starting Point (same for both):**
```
          C1 ← C2 ← C3  (feature)
         /
A ← B ← D ← E  (main)
```

---

#### Scenario 1: Rebase Feature onto Main ✅ (CORRECT - Do this!)

```bash
git checkout feature      # Go to YOUR branch
git rebase main           # Replay YOUR commits on top of main
```

**Result:**
```
A ← B ← D ← E  (main)
              \
               C1' ← C2' ← C3'  (feature) ← HEAD
```

- ✅ **main stays untouched** (safe for everyone)
- ✅ Only YOUR feature branch is rewritten
- ✅ Feature now has latest main changes
- ✅ Ready for a clean merge/PR later

---

#### Scenario 2: Rebase Main onto Feature ❌ (WRONG - Don't do this!)

```bash
git checkout main         # Go to SHARED branch
git rebase feature        # Replay main's commits on top of feature
```

**Result:**
```
A ← B ← C1 ← C2 ← C3  (feature)
                    \
                     D' ← E'  (main) ← HEAD
```

- ❌ **main is rewritten!** (D and E become D' and E')
- ❌ Everyone else's main is now incompatible
- ❌ Causes "diverged branches" errors for teammates
- ❌ May require `--force` push (destroys shared history)

---

### 🧠 How to Remember: "I Sit on the Throne"

Think of rebase as: **"I want to sit on top of the throne"**

```
git checkout <branch-I-want-to-move>   # I get up
git rebase <branch-I-want-to-sit-on>   # I sit on the throne
```

**Memory trick:**

| Command | Meaning |
|---------|---------|
| `git checkout feature` | "I am feature" |
| `git rebase main` | "I want to sit on top of main" |

So: **"Feature sits on main"** = Feature's commits move on top of main.

---

### 🎯 Quick Decision Guide

| I want to... | Command |
|--------------|---------|
| Update my feature with latest main | `git checkout feature && git rebase main` |
| Prepare feature for PR/merge | `git checkout feature && git rebase main` |
| ~~Make main have my feature commits~~ | ❌ Don't rebase! Use `git merge` instead |

**Rule of thumb:** Always rebase **your private branch** onto **the shared branch**. Never the other way around.

### Golden Rule

> **Never rebase commits that have been pushed to a shared repository.**

### Side-by-Side Comparison

| Aspect | Merge | Rebase |
|--------|-------|--------|
| **Result** | Diamond shape with merge commit | Linear chain |
| **History** | Shows parallel development | Looks like sequential work |
| **Commits** | Preserves original commits | Creates new commits (different hashes) |
| **Safe for shared branches?** | ✅ Yes | ❌ No (rewrites history) |

**Visual Summary:**

```
MERGE:                          REBASE:
      C1─C2─C3
     /        \                 A─B─D─E─C1'─C2'─C3'
A─B─D────E─────M                      (linear)
    (diamond)
```

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
