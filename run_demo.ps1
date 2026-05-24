$ErrorActionPreference = "Stop"

if (-not $env:BLENDER_EXECUTABLE) {
    $defaultBlender = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
    if (Test-Path $defaultBlender) {
        $env:BLENDER_EXECUTABLE = $defaultBlender
    }
}

.\.venv\Scripts\python.exe -B agentic_main.py `
    --input input\used_new_balance_574_classic______free.glb `
    --output outputs

# To run with reviewer corrections:
# .\.venv\Scripts\python.exe -B agentic_main.py `
#     --input input\used_new_balance_574_classic______free.glb `
#     --output outputs `
#     --review-overrides configs\review_overrides.example.json
