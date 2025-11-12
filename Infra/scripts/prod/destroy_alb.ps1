#!/usr/bin/env pwsh
# Cleanup script for ALB and Kubernetes resources before terragrunt destroy

param(
    [Parameter(Mandatory=$false)]
    [string]$Environment = "prod",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ALB and K8s Resources Cleanup Script" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Set cluster context
$clusterName = "$Environment-eks-cluster"
$region = "eu-central-1"

Write-Host "`nStep 1: Configuring kubectl context..." -ForegroundColor Green
try {
    aws eks update-kubeconfig --name $clusterName --region $region
    Write-Host "✓ Configured kubectl for cluster: $clusterName" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to configure kubectl. Cluster might already be deleted." -ForegroundColor Yellow
    if (-not $Force) {
        Write-Host "Use -Force flag to proceed with AWS resource cleanup only" -ForegroundColor Yellow
        exit 1
    }
}

# Delete Kubernetes Ingress resources that create ALBs
Write-Host "`nStep 2: Deleting Kubernetes Ingress resources..." -ForegroundColor Green
try {
    # Delete the edge ingress that creates the ALB
    kubectl delete ingress edge-to-nginx -n ingress-nginx --ignore-not-found=true
    Write-Host "✓ Deleted edge-to-nginx ingress" -ForegroundColor Green
    
    # Delete any other ingresses with ALB class
    $ingresses = kubectl get ingress -A -o json | ConvertFrom-Json
    foreach ($item in $ingresses.items) {
        if ($item.spec.ingressClassName -eq "alb") {
            Write-Host "  Deleting ingress: $($item.metadata.name) in namespace: $($item.metadata.namespace)"
            kubectl delete ingress $item.metadata.name -n $item.metadata.namespace
        }
    }
} catch {
    Write-Host "⚠ Warning: Could not delete ingresses (cluster might be down)" -ForegroundColor Yellow
}

# Wait for ALB deletion
Write-Host "`nStep 3: Waiting for ALB deletion (this may take 2-3 minutes)..." -ForegroundColor Green
Start-Sleep -Seconds 30

# Check for remaining ALBs in AWS
Write-Host "`nStep 4: Checking for remaining ALBs..." -ForegroundColor Green
$albs = aws elbv2 describe-load-balancers --region $region --query "LoadBalancers[?contains(LoadBalancerName, 'k8s-')].LoadBalancerArn" --output json | ConvertFrom-Json

if ($albs.Count -gt 0) {
    Write-Host "Found $($albs.Count) Kubernetes-managed ALB(s) still present" -ForegroundColor Yellow
    
    foreach ($albArn in $albs) {
        $albName = ($albArn -split '/')[-2]
        Write-Host "  - $albName" -ForegroundColor Yellow
        
        if ($Force) {
            Write-Host "    Forcefully deleting ALB: $albName" -ForegroundColor Red
            aws elbv2 delete-load-balancer --load-balancer-arn $albArn --region $region
        }
    }
    
    if ($Force) {
        Write-Host "Waiting additional 30 seconds for forced ALB deletion..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    } else {
        Write-Host "`n⚠ To force delete these ALBs, run: .\cleanup-alb-resources.ps1 -Force" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ No Kubernetes-managed ALBs found" -ForegroundColor Green
}

# Check for Target Groups
Write-Host "`nStep 5: Checking for orphaned Target Groups..." -ForegroundColor Green
$targetGroups = aws elbv2 describe-target-groups --region $region --query "TargetGroups[?contains(TargetGroupName, 'k8s-')].TargetGroupArn" --output json | ConvertFrom-Json

if ($targetGroups.Count -gt 0) {
    Write-Host "Found $($targetGroups.Count) Kubernetes-managed Target Group(s)" -ForegroundColor Yellow
    
    foreach ($tgArn in $targetGroups) {
        $tgName = ($tgArn -split '/')[-2]
        Write-Host "  - $tgName" -ForegroundColor Yellow
        
        if ($Force) {
            Write-Host "    Forcefully deleting Target Group: $tgName" -ForegroundColor Red
            aws elbv2 delete-target-group --target-group-arn $tgArn --region $region 2>$null
        }
    }
} else {
    Write-Host "✓ No orphaned Target Groups found" -ForegroundColor Green
}

# Check Security Groups
Write-Host "`nStep 6: Checking for ALB Security Groups..." -ForegroundColor Green
$sgQuery = "SecurityGroups[?contains(GroupName, 'k8s-elb-') || contains(GroupName, 'k8s-traffic-')]"
$securityGroups = aws ec2 describe-security-groups --region $region --query $sgQuery --output json 2>$null | ConvertFrom-Json

if ($securityGroups.Count -gt 0) {
    Write-Host "Found $($securityGroups.Count) Kubernetes-managed Security Group(s)" -ForegroundColor Yellow
    
    foreach ($sg in $securityGroups) {
        Write-Host "  - $($sg.GroupName) ($($sg.GroupId))" -ForegroundColor Yellow
        
        if ($Force) {
            Write-Host "    Forcefully deleting Security Group: $($sg.GroupName)" -ForegroundColor Red
            # First remove all ingress rules
            aws ec2 revoke-security-group-ingress --group-id $sg.GroupId --ip-permissions "$($sg.IpPermissions | ConvertTo-Json -Compress)" --region $region 2>$null
            # Then delete the security group
            aws ec2 delete-security-group --group-id $sg.GroupId --region $region 2>$null
        }
    }
} else {
    Write-Host "✓ No orphaned Security Groups found" -ForegroundColor Green
}

# Final check
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Cleanup Status Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$remainingAlbs = aws elbv2 describe-load-balancers --region $region --query "LoadBalancers[?contains(LoadBalancerName, 'k8s-')].LoadBalancerArn" --output json | ConvertFrom-Json
if ($remainingAlbs.Count -eq 0) {
    Write-Host "✓ All ALBs cleaned up successfully!" -ForegroundColor Green
    Write-Host "`nYou can now safely run: terragrunt destroy-all" -ForegroundColor Green
} else {
    Write-Host "✗ Some ALBs still remain. Run with -Force flag to delete them." -ForegroundColor Red
    Write-Host "  .\cleanup-alb-resources.ps1 -Environment $Environment -Force" -ForegroundColor Yellow
}

Write-Host "`nNote: It's recommended to wait 1-2 minutes after this script" -ForegroundColor Yellow
Write-Host "before running terragrunt destroy-all to ensure AWS has fully" -ForegroundColor Yellow
Write-Host "released all resources." -ForegroundColor Yellow