# .\k6 run -o 'dashboard=period=1s' --out 'csv=data/rust.csv' --out 'json=data/rust.json' rust.js
# .\k6 run -o 'dashboard=period=1s' --out 'csv=data/dotnet.csv' --out 'json=data/dotnet.json' dotnet.js
# .\k6 run -o 'dashboard=period=1s' --out 'csv=data/go.csv' --out 'json=data/go.json' go.js
# .\k6 run -o 'dashboard=period=1s' --out 'csv=data/python.csv' --out 'json=data/python.json' python.js
# .\k6 run -o 'dashboard=period=1s' --out 'csv=data/php.csv' --out 'json=data/php.json' php.js

k6 run --out 'csv=data/php.csv' --env LANG=php remote.js
k6 run --out 'csv=data/python.csv' --env LANG=python remote.js
k6 run --out 'csv=data/dotnet.csv' --env LANG=dotnet remote.js
k6 run --out 'csv=data/go.csv' --env LANG=go remote.js
k6 run --out 'csv=data/go-fiber.csv' --env LANG=go-fiber remote.js
k6 run --out 'csv=data/rust.csv' --env LANG=rust remote.js