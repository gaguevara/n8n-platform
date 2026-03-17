$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..\..")
$enginePath = Join-Path $projectRoot ".multiagent\core\engine.py"
$configPath = Join-Path $projectRoot ".multiagent\adapters\framework-multiagent.json"

if (-not (Test-Path $enginePath)) {
    Write-Error "No se encontro engine.py en $enginePath"
}

if (-not (Test-Path $configPath)) {
    Write-Error "No se encontro framework-multiagent.json en $configPath"
}

python $enginePath --config $configPath --base $projectRoot sync-index --write
