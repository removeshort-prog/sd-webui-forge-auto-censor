param([string]$ForgePath)

$ErrorActionPreference = 'Stop'
try {
    if (-not $ForgePath) { $ForgePath = Read-Host 'Forge Neo 根目录（包含 launch.py）' }
    $resolvedRoot = (Resolve-Path -LiteralPath $ForgePath.Trim().Trim('"')).Path
    if (-not (Test-Path (Join-Path $resolvedRoot 'launch.py')) -or
        -not (Test-Path (Join-Path $resolvedRoot 'modules'))) { throw '这不是有效的 Forge Neo 根目录。' }
    $destination = Join-Path $resolvedRoot 'extensions\sd-webui-forge-auto-censor'
    if (Test-Path $destination) { throw "插件目录已存在，请先移走旧目录：$destination" }
    New-Item -ItemType Directory -Path (Split-Path $destination) -Force | Out-Null
    Copy-Item -LiteralPath $PSScriptRoot -Destination $destination -Recurse
    Write-Host "已安装：[自动打码] -> $destination" -ForegroundColor Green
} catch { Write-Host $_.Exception.Message -ForegroundColor Red; exit 1 }
