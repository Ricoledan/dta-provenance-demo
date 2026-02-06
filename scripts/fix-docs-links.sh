#!/bin/bash
# Fix common documentation link issues

set -e

echo "🔧 Fixing documentation links..."

# Fix case-sensitive file references
find docs -name "*.md" -type f -exec sed -i '' \
  -e 's/](dta-standards\.md)/](DTA_STANDARDS.md)/g' \
  -e 's/](architecture\.md)/](ARCHITECTURE.md)/g' \
  -e 's/](comparison\.md)/](COMPARISON.md)/g' \
  -e 's/](contributing\.md)/](CONTRIBUTING.md)/g' \
  -e 's/](case-studies\.md)/](CASE_STUDIES.md)/g' \
  {} \;

# Fix relative links from quickstart (which is symlinked from README)
if [ -L docs/quickstart.md ]; then
  echo "⚠️  quickstart.md is a symlink - links may break"
  echo "   Consider copying README.md to docs/quickstart.md instead"
fi

# Fix links to files outside docs/
find docs -name "*.md" -type f -exec sed -i '' \
  -e 's|\.\./\.github/workflows/test\.yml|https://github.com/Ricoledan/dta-provenance-demo/blob/main/.github/workflows/test.yml|g' \
  -e 's|\.\./DTA_Provenance_Demo\.ipynb|https://github.com/Ricoledan/dta-provenance-demo/blob/main/DTA_Provenance_Demo.ipynb|g' \
  {} \;

echo "✅ Link fixes applied!"
echo ""
echo "Run 'mkdocs build --strict' to verify"
