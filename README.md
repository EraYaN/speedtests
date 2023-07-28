# Speed tests for a ticketing system

Run your favorite flavor of MySQL, seed the database and start the individual application services.
The `run.ps1` scripts use the excellent [xk6-dashboard](https://github.com/szkiba/xk6-dashboard) for live visualization.

## Some results

Running on a DigitalOcean Droplet with 4 cores and 8GB of RAM with a [Caddy reverse proxy](https://github.com/lucaslorentz/caddy-docker-proxy) terminating SSL.

It either quits due to to many dropped iterations > 10/s, failed requests > 10/s or a p(95) latency of higher than 500ms for more than 10 seconds. ([configuration here](./k6/shared/global-options.js#L47-L66))

They should all have a MySQL Connection Pool of 100 in total, except for PHP which does one connection per request.

| Implementation                     | Rate (/s) | Avg (ms) | Med (ms) | p(90) (ms) | p(95) (ms) | Notes                                                                                                                                     |
| ---------------------------------- | --------: | -------: | -------: | ---------: | ---------: | ----------------------------------------------------------------------------------------------------------------------------------------- |
| .NET 7.0 C# Minimal API            |     2,029 |     29.1 |     19.6 |       54.0 |       86.2 | Fails on dropped iterations.                                                                                                              |
| Rust 1.69 Axum                     |     5,045 |     22.5 |     16.5 |       28.3 |       40.9 | Fails on dropped iterations (insufficient VUs).                                                                                           |
| PHP-FPM 8.2 Slim Framework FastCGI |       348 |    140.5 |     29.1 |      372.8 |      556.8 | Pegs the CPU, but keeps working, quits on the latency bound. (5 workers)                                                                  |
| Python 3.11 FastAPI + Uvicorn      |     1,772 |     55.1 |     24.7 |      125.2 |      226.4 | Fails on dropped iterations after the latency spikes. (5 workers)                                                                         |
| Go 1.20 Gin                        |     2,605 |     46.5 |     17.5 |       94.7 |      232.8 | Long before the limit is reached, at around 1500 req/s, latency starts spiking and throughput becomes spiky. Quits on dropped iterations. |
