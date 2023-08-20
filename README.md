# Speed tests for a ticketing system

Run your favorite flavor of MySQL, seed the database and start the individual application services.
The `run.ps1` scripts use the excellent [xk6-dashboard](https://github.com/szkiba/xk6-dashboard) for live visualization (as a `k6` executable in the `k6` directory).

Add a `.speedtest_options.json` file in the `k6` directory with the following content, the tests assume all the language servers are available over https and as a subdomain on the given domain.

```json
{
  "root_domain": "your.base.domain.local"
}
```

## Some results

Running on a DigitalOcean Droplet with 4 cores and 8GB of RAM with a [Caddy reverse proxy](https://github.com/lucaslorentz/caddy-docker-proxy) terminating SSL.

It either quits due to to many dropped iterations > 500/s (max VUs 2000), failed requests > 500/s or a p(95) latency of higher than 1000ms for more than 10 seconds. ([configuration here](./k6/shared/global-options.js#L47-L66))

They should all have a MySQL Connection Pool of 100 in total, except for PHP which does one connection per request.

### Old results

| Implementation                     | Rate (/s) | Avg (ms) | Med (ms) | p(90) (ms) | p(95) (ms) | Notes                                                                                                                          |
| ---------------------------------- | --------: | -------: | -------: | ---------: | ---------: | ------------------------------------------------------------------------------------------------------------------------------ |
| PHP-FPM 8.2 Slim Framework FastCGI |       336 |    308.3 |     55.5 |      884.5 |    1,363.8 | Pegs the CPU, but keeps working, quits on the latency bound. (5 workers)                                                       |
| Python 3.11 FastAPI + Uvicorn      |     1,716 |    204.1 |     24.1 |      580.1 |    1,271.1 | Fails on latency. (5 workers)                                                                                                  |
| .NET 7.0 C# Minimal API            |     2,189 |    153.8 |     21.0 |      271.0 |    1,367.4 | Fails on latency.                                                                                                              |
| .NET 8.0 preview 6 C# Minimal API  |     2,374 |    157.1 |     20.6 |      298.2 |    1,265.1 | Fails on latency.                                                                                                              |
| Go 1.20 Gin                        |     2,850 |    177.2 |     20.1 |      325.0 |    1,283.2 | Long before the limit is reached, at around 1700 req/s, latency starts spiking and throughput becomes spiky. Quits on latency. |
| Go 1.20 Fiber                      |     2,611 |    183.9 |     20.1 |      345.8 |    1,214.2 | Long before the limit is reached, at around 1700 req/s, latency starts spiking and throughput becomes spiky. Quits on latency. |
| Rust 1.69 Axum                     |     5,025 |    107.2 |     18.0 |       65.6 |      675.3 |                                                                                                                                |

![](graphs/requests-bare-api.svg?raw=true)

### New results

After adding the templating engine (still lookup endpoint)

| Implementation                                | Rate (/s) | Avg (ms) | Med (ms) | p(90) (ms) | p(95) (ms) | Notes                                                                                  |
| --------------------------------------------- | --------: | -------: | -------: | ---------: | ---------: | -------------------------------------------------------------------------------------- |
| PHP-FPM 8.2 Slim Framework Twig FastCGI       |       183 |    208.8 |     39.5 |      822.7 |    1,229.1 | Pegs the CPU, but keeps working for some time, quits on the latency bound. (5 workers) |
| Python 3.11 Jinja2 FastAPI + Uvicorn          |     1,522 |    204.5 |     24.2 |      673.4 |    1,007.9 |                                                                                        |
| .NET 8.0 preview 6 C# Minimal API Razor Pages |     2,159 |    147.6 |     20.4 |      301.9 |      878.9 |                                                                                        |
| Go 1.20 Gin Jet                               |     2,966 |    188.4 |     20.4 |      413.2 |    1,153.2 | Quits on latency bound                                                                 |
| Go 1.20 Fiber                                 |     2,870 |    204.5 |     20.2 |      472.2 |    1,122.7 |                                                                                        |
| Rust 1.70.1 Axum Tera                         |     3,299 |    179.3 |     19.5 |      410.4 |    1,175.5 | Quits on latency bound, hits max VUs around 3.75kreq/s                                 |

![](graphs/requests-lookup.svg?raw=true)

And the template endpoint itself:

| Implementation                                | Rate (/s) | Avg (ms) | Med (ms) | p(90) (ms) | p(95) (ms) | Notes                                                                                  |
| --------------------------------------------- | --------: | -------: | -------: | ---------: | ---------: | -------------------------------------------------------------------------------------- |
| PHP-FPM 8.2 Slim Framework Twig FastCGI       |       180 |    215.6 |     42.9 |      787.6 |    1,205.9 | Pegs the CPU, but keeps working for some time, quits on the latency bound. (5 workers) |
| Python 3.11 Jinja2 FastAPI + Uvicorn          |     1,443 |    218.3 |     24.5 |      692.8 |    1,112.4 |                                                                                        |
| .NET 8.0 preview 6 C# Minimal API Razor Pages |     2,095 |    168.0 |     20.7 |      354.7 |    1,340.1 |                                                                                        |
| Go 1.20 Gin Jet                               |     2,619 |    187.0 |     20.5 |      468.2 |    1,079.5 | Quits on latency bound                                                                 |
| Rust 1.70.1 Axum Tera                         |     3,214 |    305.2 |     20.2 |      749.1 |    1,234.3 | Quits on latency bound, hits max VUs around 3.5kreq/s                                  |

![](graphs/requests-template.svg?raw=true)

## Further exploration

Some of the results are not quite that reliable, maybe switch to running locally on known hardware.

Rust: check Askama  
Python: check Tenjin  
Go: check some compiled templating  
Zig: zap or maybe the std lib?
