[Parameter(Mandatory = $false)]
        [System.Object]$telemetryClient = $null,
        [Parameter(Mandatory = $false)]
        [bool]$SkipFontImport = $false
        [bool]$SkipFontImport = $false,
        [Parameter(Mandatory = $false)]
        [bool]$throwErrors = $false
    )

    begin {
        if (! $telemetryClient) {
            $telemetryClient = Get-TelemetryClient -ErrorAction SilentlyContinue
        }
        $started = Get-Date -Format "o"
        $properties = @{ NavServiceName = $NavServiceName; ServerInstance = $ServerInstance; Tenant = $Tenant; Path = $Path; DatabaseServer = $DatabaseServer; SyncMode = $SyncMode }
    }
    
    process {
        $maxDepth = 4 # max recurse folder depth for searching Apps, FOBs, RIMs, ...
        
        # Import FOBs
        $items = @()
        if (Test-Path -LiteralPath "$Path") {
            $items = @() + (Get-ChildItem -LiteralPath "$Path" -Filter "*.fob" -Recurse -Depth $maxDepth -ErrorAction SilentlyContinue)
        }
        if ($items) {
            try {
                $started = Get-Date -Format "o"
                Write-Host "Import $($items.Length) FOBs..."
@@ -55,6 +57,9 @@
            }
            catch {
                Write-Host "Import FOBs Error: $($_.Exception.Message)" -f Red  | Out-String
                if($throwErrors) {
                    throw $_
                }
            }
            finally {
                Write-Host "Import FOBs done. (Duration: $(New-TimeSpan -start $started -end (Get-Date)))"
@@ -107,6 +112,9 @@ function Import-Artifacts {
            }
            catch {
                Write-Host "Import Apps Error: $($_.Exception.Message)" -f Red
                if($throwErrors) {
                    throw $_
                }
            }
            finally {
                Write-Host "Import Apps done. (Duration: $(New-TimeSpan -start $started -end (Get-Date)))"
@@ -134,6 +142,9 @@ function Import-Artifacts {
            }
            catch {
                Write-Host "Import RapidStart packages Error: $($_.Exception.Message)" -f Red
                if($throwErrors) {
                    throw $_
                }
            }
            finally {
                Write-Host "Import RapidStart packages done. (Duration: $(New-TimeSpan -start $started -end (Get-Date)))"
@@ -160,6 +171,9 @@ function Import-Artifacts {
            }
            catch {
                Write-Host "Import Fonts Error: $($_.Exception.Message)" -f Red  | Out-String
                if($throwErrors) {
                    throw $_
                }
            }
            finally {
                Write-Host "Import Fonts done. (Duration: $(New-TimeSpan -start $started -end (Get-Date)))"
