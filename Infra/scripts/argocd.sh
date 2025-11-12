#!/usr/bin/env bash
set -euo pipefail

NS="${1:-argocd}"
LOCAL_PORT="${2:-8080}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl not found in PATH" >&2
  exit 1
fi

# Initial admin password (may not exist if rotated)
if kubectl -n "$NS" get secret argocd-initial-admin-secret >/dev/null 2>&1; then
  PASS_B64=$(kubectl -n "$NS" get secret argocd-initial-admin-secret -o jsonpath='{.data.password}')
  PASS=$(printf '%s' "$PASS_B64" | base64 -d 2>/dev/null || true)
else
  PASS="<secret not found (maybe already changed/rotated)>"
fi

# Detect service & target port
if ! kubectl -n "$NS" get svc argocd-server >/dev/null 2>&1; then
  echo "Service 'argocd-server' not found in namespace '$NS'." >&2
  exit 1
fi

# Prefer port named 'https', else first port
TARGET_PORT=$(kubectl -n "$NS" get svc argocd-server -o jsonpath='{range .spec.ports[?(@.name=="https")]}{.port}{end}')
if [[ -z "${TARGET_PORT}" ]]; then
  TARGET_PORT=$(kubectl -n "$NS" get svc argocd-server -o jsonpath='{.spec.ports[0].port}')
fi

SCHEME="http"
[[ "$TARGET_PORT" == "443" ]] && SCHEME="https"

echo
echo "Argo CD login:"
echo "  Username : admin"
echo "  Password : $PASS"
echo "  URL      : ${SCHEME}://localhost:${LOCAL_PORT}"

echo
echo "Starting port-forward: local ${LOCAL_PORT} -> svc/argocd-server:${TARGET_PORT} (ns: ${NS})"
kubectl -n "$NS" port-forward svc/argocd-server "${LOCAL_PORT}:${TARGET_PORT}"
