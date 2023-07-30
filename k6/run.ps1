param (
    [Parameter(Mandatory=$true)][string]$lang
 )

.\k6 run -o 'dashboard=open=true&period=1s' --out "csv=data/$lang.csv" --env LANG=$lang remote.js