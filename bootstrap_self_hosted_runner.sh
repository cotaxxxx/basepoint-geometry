#!/usr/bin/env bash
set -Eeuo pipefail

REPO="cotaxxxx/daybreak-works-control"
CONTROL="$HOME/daybreak-works-control"
RUNNER="$HOME/actions-runner-daybreak"
LABEL="daybreak-works"
NAME="daybreak-works"

say(){ printf '\n== %s ==\n' "$*"; }
fail(){ printf '\nFAIL: %s\n' "$*" >&2; exit 1; }

command -v git >/dev/null || fail "git is required"
command -v curl >/dev/null || fail "curl is required"

if ! command -v gh >/dev/null 2>&1; then
  say "Install GitHub CLI (one time)"
  sudo apt-get update
  sudo apt-get install -y gh
fi

if ! gh auth status >/dev/null 2>&1; then
  say "Authorize this research PC with GitHub (one time)"
  printf 'Approve the GitHub device authorization once.\n'
  gh auth login --hostname github.com --git-protocol https --web
  gh auth setup-git
fi

gh auth status >/dev/null 2>&1 || fail "GitHub CLI authentication did not complete"

# Workflow files require the OAuth 'workflow' scope. Add it only when missing.
if ! gh api -i user 2>/dev/null | tr -d '\r' | grep -qi '^x-oauth-scopes:.*workflow'; then
  say "Authorize GitHub workflow scope (one time)"
  gh auth refresh --hostname github.com --scopes workflow
  gh auth setup-git
fi

say "Prepare private control repository"
if gh repo view "$REPO" >/dev/null 2>&1; then
  VIS="$(gh repo view "$REPO" --json visibility --jq .visibility)"
  [[ "$VIS" == "PRIVATE" ]] || fail "$REPO exists but is not private"
else
  gh repo create "$REPO" --private
fi

# Resume cleanly after a previous rejected push.
if [[ ! -d "$CONTROL/.git" ]]; then
  rm -rf "$CONTROL"
  mkdir -p "$CONTROL/.github/workflows" "$CONTROL/jobs" "$CONTROL/results"
  cd "$CONTROL"
  git init -b main
  git config user.name "daybreak-runner-bootstrap"
  git config user.email "runner@localhost"
else
  cd "$CONTROL"
fi

mkdir -p .github/workflows jobs results
cat > .github/workflows/remote.yml <<'YAML'
name: DAYBREAK PC remote job

on:
  push:
    branches: [main]
    paths:
      - jobs/run.sh

permissions:
  contents: write

concurrency:
  group: daybreak-pc-remote
  cancel-in-progress: false

jobs:
  remote:
    runs-on: [self-hosted, Linux, X64, daybreak-works]
    timeout-minutes: 360
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
        with:
          persist-credentials: true
          fetch-depth: 1

      - name: Execute requested job
        id: execute
        continue-on-error: true
        shell: bash
        run: |
          set +e
          mkdir -p results
          {
            echo "STARTED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
            echo "HOST=$(hostname)"
            echo "USER=$(id -un)"
            echo "PWD=$(pwd)"
            echo "--- OUTPUT ---"
            bash jobs/run.sh
          } > results/latest.log 2>&1
          rc=$?
          printf '%s\n' "$rc" > results/latest.exitcode
          echo "FINISHED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> results/latest.log
          echo "EXIT_CODE=$rc" >> results/latest.log
          echo "rc=$rc" >> "$GITHUB_OUTPUT"
          exit "$rc"

      - name: Commit result
        if: always()
        shell: bash
        run: |
          set -euo pipefail
          git config user.name "daybreak-works-runner"
          git config user.email "runner@localhost"
          git add results/latest.log results/latest.exitcode
          if ! git diff --cached --quiet; then
            git commit -m "runner result ${GITHUB_SHA}"
            git push origin HEAD:main
          fi

      - name: Propagate command status
        if: always()
        shell: bash
        run: exit "${{ steps.execute.outputs.rc || '1' }}"
YAML

cat > jobs/run.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
echo "RUNNER_ONLINE_TEST"
uname -a
whoami
pwd
command -v python >/dev/null && python --version || true
SH
chmod +x jobs/run.sh
printf '# DAYBREAK works control\nPrivate control repository for the dedicated self-hosted research PC.\n' > README.md
: > results/.gitkeep

git config user.name "daybreak-runner-bootstrap"
git config user.email "runner@localhost"
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "https://github.com/${REPO}.git"
fi
git add .
if ! git diff --cached --quiet; then
  git commit -m "Initialize private DAYBREAK PC control"
fi
git push -u origin main

say "Install GitHub Actions runner locally"
mkdir -p "$RUNNER"
cd "$RUNNER"
if [[ ! -x ./config.sh ]]; then
  VERSION="$(gh api repos/actions/runner/releases/latest --jq .tag_name | sed 's/^v//')"
  ARCHIVE="actions-runner-linux-x64-${VERSION}.tar.gz"
  URL="https://github.com/actions/runner/releases/download/v${VERSION}/${ARCHIVE}"
  curl -fL --retry 3 -o "$ARCHIVE" "$URL"
  tar xzf "$ARCHIVE"
  rm -f "$ARCHIVE"
fi

if [[ ! -f .runner ]]; then
  TOKEN="$(gh api -X POST "repos/${REPO}/actions/runners/registration-token" --jq .token)"
  ./config.sh --unattended --replace \
    --url "https://github.com/${REPO}" \
    --token "$TOKEN" \
    --name "$NAME" \
    --labels "$LABEL" \
    --work _work
  unset TOKEN
fi

say "Install boot-time runner service"
if [[ -x ./svc.sh ]]; then
  if ! systemctl list-unit-files --type=service 2>/dev/null | grep -q 'actions.runner.*daybreak'; then
    sudo ./svc.sh install "$(id -un)"
  fi
  sudo ./svc.sh start
  sleep 3
  PERSISTENCE="system service (starts at boot; desktop login not required)"
else
  fail "runner svc.sh is missing"
fi

say "Disable suspend and hibernate for always-on operation"
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target >/dev/null

say "Verify runner registration"
gh api "repos/${REPO}/actions/runners" --jq '.runners[] | {name,status,busy,labels:[.labels[].name]}'

echo
printf 'READY: %s\n' "$REPO"
printf 'RUNNER_DIR: %s\n' "$RUNNER"
printf 'PERSISTENCE: %s\n' "$PERSISTENCE"
printf 'POWER: suspend/hibernate disabled; screen lock is harmless\n'
printf 'NOTE: ChatGPT does not need to be opened on this PC. Leave it powered on and use the phone for conversation.\n'
