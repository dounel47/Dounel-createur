# Script de instalación de MongoDB Compass

# URL de descarga de MongoDB Compass
$mongoCompassUrl = "https://downloads.mongodb.com/compass/mongodb-compass-1.40.4-win32-x64.exe"
$outputDir = "$env:USERPROFILE\Downloads"
$mongoCompassInstaller = "$outputDir\mongodb-compass-installer.exe"

# Descargar MongoDB Compass
Write-Host "Descargando MongoDB Compass..."
Invoke-WebRequest -Uri $mongoCompassUrl -OutFile $mongoCompassInstaller

# Instalar MongoDB Compass
Write-Host "Instalando MongoDB Compass..."
Start-Process -FilePath $mongoCompassInstaller -ArgumentList "/S" -Wait

Write-Host "Instalación completada. Reinicie su sistema para aplicar cambios."
