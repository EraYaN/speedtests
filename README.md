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

After adding the templating engine (still lookup endpoint)

| Implementation                          | Rate (/s) | Avg (ms) | Med (ms) | p(90) (ms) | p(95) (ms) | Notes                                                                    |
| --------------------------------------- | --------: | -------: | -------: | ---------: | ---------: | ------------------------------------------------------------------------ |
| PHP-FPM 8.2 Slim Framework Twig FastCGI |       198 |    197.0 |     39.3 |      745.1 |    1,145.6 | Pegs the CPU, but keeps working, quits on the latency bound. (5 workers) |

And the template endpoint itself:

| Implementation                          | Rate (/s) | Avg (ms) | Med (ms) | p(90) (ms) | p(95) (ms) | Notes                                                                    |
| --------------------------------------- | --------: | -------: | -------: | ---------: | ---------: | ------------------------------------------------------------------------ |
| PHP-FPM 8.2 Slim Framework Twig FastCGI |       171 |  197.0 |    41.9 |  761.1 | 1,159.3 | Pegs the CPU, but keeps working, quits on the latency bound. (5 workers) |
