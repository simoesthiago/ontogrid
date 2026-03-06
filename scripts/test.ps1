$ErrorActionPreference = "Stop"

Push-Location "src/backend"
try {
    pytest
}
finally {
    Pop-Location
}
