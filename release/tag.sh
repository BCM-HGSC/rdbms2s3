#!/usr/bin/env bash

set -e

OLD_TAG="$1"
NEW_VERSION="$2"

if ! git tag | fgrep "$OLD_TAG" >/dev/null; then
    echo "The tag $OLD_TAG does not exist."
    exit 2
fi

echo "Will release v$NEW_VERSION following $OLD_TAG"

echo "Updating local from origin..."
git fetch origin
git checkout main
git reset --hard origin/main

echo
echo "Updating version strings..."
sed -i.tmp "s/^\*\*Version:\*\*..*/**Version:** $NEW_VERSION/" README.md
sed -i.tmp "s/^__version__..*/__version__ = \"$NEW_VERSION\"/" version.py
rm README.md.tmp version.py.tmp

echo
echo "Commiting local changes..."
git add README.md version.py
git commit -m "Bump version to $NEW_VERSION"

echo
echo "Creating release tag..."

cat <<EOD > TMP_MESSAGE
This is the release v${NEW_VERSION}.
This release includes these changes:
EOD

git log --format='%H %s' --grep Bump --no-decorate  |
    fgrep $OLD_TAG |
    cut -d' ' -f1 |
    xargs -n1 git log -n1 --format=$'\n\n## %s\n\n%b' >> TMP_MESSAGE

git tag -ef v$NEW_VERSION --cleanup=verbatim -F TMP_MESSAGE

echo
echo "Your new release tag, ready to publish:"
echo
git show v$NEW_VERSION



