k6 run --out 'csv=data/php-lookup.csv' --env LANG=php --env ENDPOINT=lookup remote.js
k6 run --out 'csv=data/php-template.csv' --env LANG=php --env ENDPOINT=template remote.js

k6 run --out 'csv=data/python-lookup.csv' --env LANG=python --env ENDPOINT=lookup remote.js
k6 run --out 'csv=data/python-template.csv' --env LANG=python --env ENDPOINT=template remote.js

k6 run --out 'csv=data/dotnet-lookup.csv' --env LANG=dotnet --env ENDPOINT=lookup remote.js
k6 run --out 'csv=data/dotnet-template.csv' --env LANG=dotnet --env ENDPOINT=template remote.js

k6 run --out 'csv=data/go-lookup.csv' --env LANG=go --env ENDPOINT=lookup remote.js
k6 run --out 'csv=data/go-template.csv' --env LANG=go --env ENDPOINT=template remote.js

k6 run --out 'csv=data/go-fiber-lookup.csv' --env LANG=go-fiber --env ENDPOINT=lookup remote.js

k6 run --out 'csv=data/rust-lookup.csv' --env LANG=rust --env ENDPOINT=lookup remote.js
k6 run --out 'csv=data/rust-template.csv' --env LANG=rust --env ENDPOINT=template remote.js