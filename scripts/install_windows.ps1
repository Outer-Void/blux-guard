# PowerShell installer for BLUX Guard Developer Suite
python -m pip install --upgrade pip
pip install .
$profilePath = $PROFILE
if (!(Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force | Out-Null
}
$aliasLine = "Set-Alias -Name bluxq -Value 'python -m blux_guard.cli.bluxq'"
if (-not (Select-String -Path $profilePath -Pattern "blux_guard" -Quiet)) {
    Add-Content -Path $profilePath -Value $aliasLine
}
Write-Output "BLUX Guard Windows installer completed."
