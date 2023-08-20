param (
    [Parameter(Mandatory=$true)][string]$lang,
    [Parameter(Mandatory=$true)][ValidateSet('lookup','template')][string]$endpoint = 'lookup'
 )

.\k6 run -o 'dashboard=open=true&period=1s' --out "csv=data/$lang-$endpoint.csv" --env LANG=$lang --env ENDPOINT=$endpoint remote.js