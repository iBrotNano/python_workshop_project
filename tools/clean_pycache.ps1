# This script will find all __pycache__ directories in the current directory and its subdirectories, and ask the user if they want to remove them.
# Execute from the root of the project to clean all __pycache__ directories in the project.
# Example usage: .\tools\clean_pycache.ps1

$pycacheDirs = Get-ChildItem -Path . -Directory -Recurse -Force -Filter "__pycache__"
$pycacheDirs | Select-Object -ExpandProperty FullName

if ((Read-Host "Do you want to remove these __pycache__ directories? (y/n)") -eq "y") {
    $pycacheDirs | Remove-Item -Recurse -Force
}