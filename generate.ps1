$sourceDir = "src/ui"
$targetDir = "src/ui"

if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir
}

$uiFiles = Get-ChildItem -Path $sourceDir -Filter "*.ui" -Recurse

foreach ($file in $uiFiles) {

    $fileNameWithoutExt = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    
    $outputFile = Join-Path $targetDir "ui_$fileNameWithoutExt.py"
    
    Write-Host "Generating $outputFile from $file"
    & pyside6-uic $file.FullName -o $outputFile
}

Write-Host "Generating resources_rc.py" 
& pyside6-rcc ./src/assets/resources.qrc -o ./src/assets/resources_rc.py