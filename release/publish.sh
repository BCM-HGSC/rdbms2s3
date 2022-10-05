#!/usr/bin/env bash

set -e

TARGET_BRANCH="$1"

RELEASE_TAG=$(git show --decorate | head -n1 | sed 's/.*tag: v/v/;s/,.*//;s/)$//')
NEW_VERSION="${RELEASE_TAG:1}+dev"

if git tag | fgrep "$RELEASE_TAG" >/dev/null; then
    echo "Using tag $RELEASE_TAG"
    echo "Bumping to version $NEW_VERSION"
    if [[ "$TARGET_BRANCH" ]]; then
        echo "Will update $TARGET_BRANCH"
    fi
else
    echo "The tag $RELEASE_TAG does not exist."
    exit 2
fi

echo
echo "Pushing master and $RELEASE_TAG..."
git push -f origin main
git push -f origin $RELEASE_TAG

if [[ "$TARGET_BRANCH" ]]; then
    echo
    echo "Publishing $TARGET_BRANCH..."
    git push -f origin HEAD:$TARGET_BRANCH
fi

echo
echo "Pushing version bump $NEW_VERSION..."
sed -i.tmp "s/^\*\*Version:\*\*..*/**Version:** $NEW_VERSION/" README.md
sed -i.tmp "s/^__version__..*/__version__ = \"$NEW_VERSION\"/" version.py
rm README.md.tmp version.py.tmp
git add README.md version.py
git commit -m "Bump version to $NEW_VERSION"
git push origin

if which pbcopy &>/dev/null; then
    echo
    git tag -l --format='%(contents)' "$RELEASE_TAG" | pbcopy
    echo "The release notes from the tag are now in the system clipboard."
    echo
fi

if which open &>/dev/null; then
    open "https://github.com/BCM-HGSC/rdbms2s3/releases/new?tag=$RELEASE_TAG"
fi
