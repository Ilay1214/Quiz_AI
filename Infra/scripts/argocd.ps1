param(
  [string]$Namespace = "argocd",
  [int]$LocalPort = 8080
)

# Fail fast
$ErrorActionPreference = "Stop"

# Ensure kubectl exists
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
  Write-Error "kubectl not found in PATH."
  exit 1
}

# Get initial admin password (if the secret exists)
try {
  $Pwd = kubectl -n $Namespace get secret argocd-initial-admin-secret `
    -o jsonpath="{.data.password}" 2>$null
  if ($Pwd) {
    $Pwd = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($Pwd))
  } else {
    $Pwd = "<secret not found (maybe already changed/rotated)>"
  }
} catch {
  $Pwd = "<secret not found (maybe already changed/rotated)>"
}

# Detect target port from Service (prefer named 'https', fallback to first port)
$svcJson = kubectl -n $Namespace get svc argocd-server -o json 2>$null
if (-not $svcJson) {
  Write-Error "Service 'argocd-server' not found in namespace '$Namespace'."
  exit 1
}
$svc = $svcJson | ConvertFrom-Json
$ports = $svc.spec.ports
$httpsPort = ($ports | Where-Object { $_.name -eq "https" } | Select-Object -First 1).port
if (-not $httpsPort) { $httpsPort = ($ports | Select-Object -First 1).port }
$scheme = if ($httpsPort -eq 443) { "https" } else { "http" }

# Output creds & URL
Write-Host "`nArgo CD login:" -ForegroundColor Cyan
Write-Host ("  Username : admin")
Write-Host ("  Password : {0}" -f $Pwd)
Write-Host ("  URL      : {0}://localhost:{1}" -f $scheme, $LocalPort)

# Port-forward (blocks in foreground)
Write-Host "`nStarting port-forward: local $LocalPort -> svc/argocd-server:$httpsPort (ns: $Namespace)`n" -ForegroundColor Yellow
kubectl -n $Namespace port-forward svc/argocd-server "$LocalPort:$httpsPort"
