$ErrorActionPreference = "Stop"

Push-Location "src/backend"
try {
    python -m pytest
}
finally {
    Pop-Location
}
