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
command -v gh >/dev/null || fail "GitHub CLI (gh) is not installed"
gh auth status >/dev/null 2>&1 || fail "GitHub CLI is not authenticated. Run: gh auth login"

say "Create private control repository"
if gh repo view "$REPO" >/dev/null 2>&1; then
  VIS="$(gh repo view "$REPO" --json visibility --jq .visibility)"
  [[ "$VIS" == "PRIVATE" ]] || fail "$REPO exists but is not private"
else
  rm -rf "$CONTROL"
  mkdir -p "$CONTROL/.github/workflows" "$CONTROL/jobs" "$CONTROL/results"
  cd "$CONTROL"
  git init -b main
  git config user.name "daybreak-runner-bootstrap"
  git config user.email "runner@localhost"

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
  git add .
  git commit -m "Initialize private DAYBREAK PC control"
  gh repo create "$REPO" --private --source=. --remote=origin --push
fi

if [[ ! -d "$CONTROL/.git" ]]; then
  rm -rf "$CONTROL"
  gh repo clone "$REPO" "$CONTROL"
fi

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

say "Start runner"
if pgrep -f "$RUNNER/bin/Runner.Listener" >/dev/null 2>&1; then
  echo "runner already running"
else
  nohup "$RUNNER/run.sh" > "$RUNNER/runner.log" 2>&1 < /dev/null &
  sleep 3
fi

say "Verify runner registration"
gh api "repos/${REPO}/actions/runners" --jq '.runners[] | {name,status,busy,labels:[.labels[].name]}'

echo
printf 'READY: %s\n' "$REPO"
printf 'RUNNER_DIR: %s\n' "$RUNNER"
printf 'LOG: %s\n' "$RUNNER/runner.log"
printf 'NOTE: runner currently starts with nohup; it will need to be restarted after a reboot until persistence is configured.\n'
