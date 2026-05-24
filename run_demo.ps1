$ErrorActionPreference = "Stop"

if (-not $env:BLENDER_EXECUTABLE) {
    $defaultBlender = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
    if (Test-Path $defaultBlender) {
        $env:BLENDER_EXECUTABLE = $defaultBlender
    }
}

$inputs = @(
    "input\used_new_balance_574_classic______free.glb",
    "input\flower_sneakers_shoe_scan.glb",
    "input\miles_morales_shoes.glb"
)

$pythonExe = ".\.venv\Scripts\python.exe"
if (Test-Path ".\.venv310\Scripts\python.exe") {
    $pythonExe = ".\.venv310\Scripts\python.exe"
}

foreach ($inputPath in $inputs) {
    $name = [System.IO.Path]::GetFileNameWithoutExtension($inputPath)
    $outputDir = "outputs\samples\$name"

    Write-Host ""
    Write-Host "Generating TechPack for $name"

    & $pythonExe -B agentic_main.py `
        --input $inputPath `
        --output $outputDir
}

# To run one sample with reviewer corrections:
# .\.venv310\Scripts\python.exe -B agentic_main.py `
#     --input input\used_new_balance_574_classic______free.glb `
#     --output outputs\samples\used_new_balance_574_classic______free `
#     --review-overrides configs\review_overrides.example.json
