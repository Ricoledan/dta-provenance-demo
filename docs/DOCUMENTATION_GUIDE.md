# Documentation Guide

How to lint, preview, and ensure documentation quality.

## Local Preview

### Start Development Server

```bash
# Install dependencies
pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin

# Start live preview server
mkdocs serve

# Open in browser
open http://127.0.0.1:8000
```

The server auto-reloads when you save changes to markdown files.

### Build Documentation

```bash
# Build static site
mkdocs build

# Build and check for errors
mkdocs build --strict

# View built site
open site/index.html
```

## Linting & Validation

### Check for Broken Links

```bash
# Build with strict mode (fails on warnings)
mkdocs build --strict

# This will show:
# - Broken internal links
# - Missing files
# - Invalid anchors
# - Incorrect references
```

### Common Issues

#### 1. Case-Sensitive File References

❌ **Wrong:**
```markdown
[DTA Standards](DTA_STANDARDS.md)
```

✅ **Correct:**
```markdown
[DTA Standards](DTA_STANDARDS.md)
```

**Files in docs/ directory:**
- `ARCHITECTURE.md` (uppercase)
- `COMPARISON.md` (uppercase)
- `CONTRIBUTING.md` (uppercase)
- `DTA_STANDARDS.md` (uppercase with underscore)
- All other files (lowercase)

#### 2. Relative Links from Symlinks

When `quickstart.md` is a symlink to `../README.md`, internal links break.

❌ **Wrong (in README.md):**
```markdown
[Architecture](docs/ARCHITECTURE.md)
```

✅ **Correct (when used as docs/quickstart.md):**
```markdown
[Architecture](ARCHITECTURE.md)
```

#### 3. External File References

Files outside `docs/` won't be included in the site.

❌ **Won't work:**
```markdown
[Jupyter Notebook](https://github.com/Ricoledan/dta-provenance-demo/blob/main/DTA_Provenance_Demo.ipynb)
```

✅ **Better:**
```markdown
View the [Jupyter Notebook on GitHub](https://github.com/Ricoledan/dta-provenance-demo/blob/main/DTA_Provenance_Demo.ipynb)
```

## Markdown Linting

### Install markdownlint

```bash
# NPM
npm install -g markdownlint-cli

# Or use Python version
pip install mdformat mdformat-gfm mdformat-myst
```

### Lint Markdown Files

```bash
# Check all markdown files
markdownlint docs/**/*.md

# Fix automatically
markdownlint --fix docs/**/*.md

# Or with Python mdformat
mdformat docs/
```

### Common Markdown Issues

1. **Inconsistent heading levels**
2. **Missing blank lines around lists**
3. **Trailing whitespace**
4. **Inconsistent list markers**
5. **Long lines (>80 chars)**

## Link Checking Tools

### Use linkchecker

```bash
# Install
pip install linkchecker

# Build and check
mkdocs build
linkchecker site/index.html

# Or check live site
linkchecker https://ricoledan.github.io/dta-provenance-demo
```

### Check External Links

```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check all files
find docs -name "*.md" -exec markdown-link-check {} \;
```

## Pre-Commit Hooks

### Create `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.39.0
    hooks:
      - id: markdownlint
        args: ['--fix']

  - repo: local
    hooks:
      - id: mkdocs-build
        name: MkDocs Build Check
        entry: mkdocs build --strict
        language: system
        pass_filenames: false
```

### Install and Use

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Documentation Quality Checklist

### Before Committing

- [ ] Run `mkdocs serve` and check pages locally
- [ ] Run `mkdocs build --strict` to catch warnings
- [ ] Check all internal links work
- [ ] Verify code blocks have correct language tags
- [ ] Ensure images/diagrams display correctly
- [ ] Test responsive design (mobile view)
- [ ] Verify dark/light mode both work

### Content Quality

- [ ] Clear, concise headings
- [ ] Proper use of formatting (bold, italic, code)
- [ ] Code examples are tested
- [ ] Links are descriptive (not "click here")
- [ ] Consistent terminology
- [ ] Proper spelling and grammar

### Navigation

- [ ] All pages accessible from nav
- [ ] Logical page hierarchy
- [ ] Breadcrumb trail makes sense
- [ ] Search works for key terms

## Automated Checks in CI

### GitHub Actions

The `.github/workflows/docs.yml` workflow:

1. ✅ Builds documentation
2. ✅ Checks for warnings
3. ✅ Deploys to GitHub Pages

### Add Link Checking

Add to `.github/workflows/docs.yml`:

```yaml
- name: Check links
  run: |
    pip install linkchecker
    linkchecker site/ --no-warnings
```

## Common Fixes

### Fix Case-Sensitive Links

```bash
# Find all lowercase references to uppercase files
grep -r "dta-standards.md" docs/
grep -r "architecture.md" docs/
grep -r "comparison.md" docs/
grep -r "contributing.md" docs/

# Replace with correct case
# Use your editor's find/replace or sed
```

### Fix Relative Path Issues

```bash
# Check symlinks
ls -la docs/*.md | grep "^l"

# If symlinks are problematic, copy files instead:
cp README.md docs/quickstart.md
cp NIX_SETUP.md docs/nix-setup.md
cp DOCKER.md docs/docker-setup.md
```

### Validate Anchors

```bash
# Check for broken anchor links
mkdocs build 2>&1 | grep "anchor"
```

## Best Practices

### File Naming

- Use lowercase with hyphens: `file-name.md`
- Or uppercase with underscores: `FILE_NAME.md`
- Be consistent within each directory

### Link Formatting

```markdown
<!-- Internal docs links -->
[Link Text](other-page.md)

<!-- Section anchors -->
[Section Link](#section-heading)

<!-- External links -->
[External](https://example.com)

<!-- GitHub repo links -->
[File on GitHub](https://github.com/user/repo/blob/main/file.md)
```

### Code Blocks

Always specify language:

````markdown
```python
print("Hello, World!")
```

```bash
echo "Hello, World!"
```

```javascript
console.log("Hello, World!");
```
````

### Mermaid Diagrams

Test locally before committing:

````markdown
```mermaid
graph LR
    A[Start] --> B[End]
```
````

## Troubleshooting

### Server Won't Start

```bash
# Kill existing process
pkill -f "mkdocs serve"

# Check port availability
lsof -i :8000

# Use different port
mkdocs serve --dev-addr=127.0.0.1:8001
```

### Broken Links After Deploy

1. Check file exists in docs/
2. Verify case matches exactly
3. Test with `mkdocs build --strict`
4. Check GitHub Pages build log

### Mermaid Diagrams Not Rendering

1. Check plugin is installed
2. Verify mkdocs.yml config
3. Test diagram syntax online: https://mermaid.live
4. Ensure proper fence formatting

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material Theme](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Mermaid Docs](https://mermaid.js.org/)

---

**Questions?** See [Contributing Guide](CONTRIBUTING.md)
