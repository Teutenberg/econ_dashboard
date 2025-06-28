# Check if Python is installed
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH. Please install Python first."
    exit 1
}

# Define the directory for the virtual environment
$venvPath = ".\venv"

# Create virtual environment if it doesn't exist
if (!(Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at '$venvPath'..."
    python -m venv $venvPath
} else {
    Write-Host "Virtual environment already exists at '$venvPath'"
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
$activateScript = "$venvPath\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Error "Activation script not found at: $activateScript"
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install/upgrade packages from requirements.txt if it exists
if (Test-Path "requirements.txt") {
    Write-Host "Installing/upgrading packages from requirements.txt..."
    pip install -r requirements.txt --upgrade
} else {
    Write-Host "No requirements.txt found. Skipping package installation."
}

Write-Host "Virtual environment setup complete!"
