[CmdletBinding()]
param(
    [string]$ProjectRoot = $env:AUTOPROOF_PROJECT,
    [string]$InputDir = "",
    [string]$OutputDir = "",
    [string]$ReportsDir = "",
    [switch]$NoOcr,
    [switch]$NoRender,
    [int]$Limit = 0,
    [string]$Only = "",
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    if (Test-Path -LiteralPath (Join-Path (Get-Location) "main.py")) {
        $ProjectRoot = (Get-Location).Path
    }
    else {
        throw "请设置 AUTOPROOF_PROJECT，或传入 -ProjectRoot 指向包含 main.py 的项目目录。"
    }
}

$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$MainPy = Join-Path $ProjectRoot "main.py"
if (-not (Test-Path -LiteralPath $MainPy)) {
    throw "项目目录中没有 main.py：$ProjectRoot"
}

if ([string]::IsNullOrWhiteSpace($InputDir)) { $InputDir = Join-Path $ProjectRoot "input" }
if ([string]::IsNullOrWhiteSpace($OutputDir)) { $OutputDir = Join-Path $ProjectRoot "output" }
if ([string]::IsNullOrWhiteSpace($ReportsDir)) { $ReportsDir = Join-Path $ProjectRoot "reports" }

if (-not (Test-Path -LiteralPath $InputDir)) {
    throw "输入目录不存在：$InputDir"
}
$InputDir = (Resolve-Path -LiteralPath $InputDir).Path
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)
$ReportsDir = [System.IO.Path]::GetFullPath($ReportsDir)

if ([string]::IsNullOrWhiteSpace($Python)) {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $Python = "python"
    }
    elseif (Get-Command py -ErrorAction SilentlyContinue) {
        $Python = "py"
    }
    else {
        throw "找不到 Python。请安装 Python 3.10+，或传入 -Python 指向 python.exe。"
    }
}

$cliArgs = @(
    $MainPy,
    "--input", $InputDir,
    "--output", $OutputDir,
    "--reports", $ReportsDir
)
if ($NoOcr) { $cliArgs += "--no-ocr" }
if ($NoRender) { $cliArgs += "--no-render" }
if ($Limit -gt 0) { $cliArgs += @("--limit", [string]$Limit) }
if (-not [string]::IsNullOrWhiteSpace($Only)) { $cliArgs += @("--only", $Only) }

Write-Host "项目：$ProjectRoot"
Write-Host "输入：$InputDir"
Write-Host "输出：$OutputDir"
Write-Host "报告：$ReportsDir"
Write-Host "OCR：$([bool](-not $NoOcr))（--no-ocr 可关闭）"
Write-Host ""

$started = Get-Date
& $Python @cliArgs
$exitCode = $LASTEXITCODE
$elapsed = (Get-Date) - $started

Write-Host ""
Write-Host ("运行结束：exit={0}，耗时 {1:N1} 秒" -f $exitCode, $elapsed.TotalSeconds)
Write-Host "先看：$(Join-Path $ReportsDir 'pairing_report.txt')"
exit $exitCode
