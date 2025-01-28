# Script de instalación de MongoDB para Windows

# Descargar el instalador de MongoDB
$mongoUrl = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.5-signed.msi"
$outputDir = "$env:USERPROFILE\Downloads"
$mongoInstaller = "$outputDir\mongodb-installer.msi"

# Descargar MongoDB
Write-Host "Descargando MongoDB..."
Invoke-WebRequest -Uri $mongoUrl -OutFile $mongoInstaller

# Instalar MongoDB
Write-Host "Instalando MongoDB..."
Start-Process msiexec.exe -Wait -ArgumentList "/i $mongoInstaller /qn ADDLOCAL=All"

# Crear directorio de datos
$dataDir = "C:\data\db"
if (!(Test-Path -Path $dataDir)) {
    New-Item -ItemType Directory -Force -Path $dataDir
}

# Añadir MongoDB al PATH
$env:Path += ";C:\Program Files\MongoDB\Server\7.0\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path, "Machine")

Write-Host "Instalación completada. Reinicie su sistema para aplicar cambios."
