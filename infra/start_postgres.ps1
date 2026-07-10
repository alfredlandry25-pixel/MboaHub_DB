$ErrorActionPreference = 'Stop'

$pgHome = 'C:\Users\Administrator\Desktop\MBOAHUB\tools\pgsql'
$binDir = Join-Path $pgHome 'bin'
$dataDir = 'C:\Users\Administrator\Desktop\MBOAHUB\infra\data'
$logFile = 'C:\Users\Administrator\Desktop\MBOAHUB\infra\postgres.log'
$schemaFile = 'C:\Users\Administrator\Desktop\MBOAHUB\infra\initdb\01_schema.sql'

$env:Path = "$binDir;$env:Path"

if (-not (Test-Path $dataDir)) {
    Write-Host 'Initializing PostgreSQL data directory...'
    & "$binDir\initdb.exe" -D $dataDir -U postgres -A trust --auth-local=trust --auth-host=trust | Out-Null

    $pgConf = Join-Path $dataDir 'postgresql.conf'
    $hbaConf = Join-Path $dataDir 'pg_hba.conf'

    Add-Content -Path $pgConf -Value "`nlisten_addresses = 'localhost'`nport = 5432`n"

    $hba = Get-Content $hbaConf
    $hba = $hba -replace "host\s+all\s+all\s+127\.0\.0\.1/32\s+scram-sha-256", "host    all             all             127.0.0.1/32            trust"
    $hba = $hba -replace "host\s+all\s+all\s+::1/128\s+scram-sha-256", "host    all             all             ::1/128                 trust"
    Set-Content -Path $hbaConf -Value $hba
}

$ready = & "$binDir\pg_isready.exe" -h localhost -p 5432 -U postgres 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Starting PostgreSQL server...'
    & "$binDir\pg_ctl.exe" -D $dataDir -l $logFile start -w | Out-Null
}

Write-Host 'Creating database role and database if needed...'
$createRole = @"
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'mboahub') THEN
    CREATE ROLE mboahub WITH LOGIN PASSWORD 'mboahub123';
  END IF;
END
$$;
"@

$createDb = @"
SELECT 'CREATE DATABASE mboahub OWNER mboahub'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mboahub')\gexec
"@

& "$binDir\psql.exe" -h localhost -U postgres -d postgres -c $createRole | Out-Null
& "$binDir\psql.exe" -h localhost -U postgres -d postgres -c $createDb | Out-Null

Write-Host 'Applying schema...'
Get-Content $schemaFile | & "$binDir\psql.exe" -h localhost -U postgres -d mboahub

Write-Host 'PostgreSQL is ready.'
Write-Host 'Connection string: postgresql://mboahub:mboahub123@localhost:5432/mboahub'
