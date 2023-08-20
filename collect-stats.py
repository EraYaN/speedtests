import json
import pandas as pd
import os.path

import matplotlib.pyplot as plt

endpoints = [
    "lookup", 
    "template"
    ]

languages = [
    "php",
    "python",
    "dotnet",
    "go",
    "go-fiber",
    "rust",
]

implementations = {
    "php": "PHP-FPM 8.2 Slim Framework Twig FastCGI",
    "python": "Python 3.11 Jinja2 FastAPI + Uvicorn",
    "dotnet": ".NET 8.0 preview 6 C# Minimal API Razor Pages",
    "go": "Go 1.20 Gin Jet",
    "go-fiber": "Go 1.20 Fiber",
    "rust": "Rust 1.70.1 Axum Tera",
}

notes = {
    "php": {
        "lookup": "Pegs the CPU, but keeps working for some time, quits on the latency bound. (5 workers)",
        "template": "Pegs the CPU, but keeps working for some time, quits on the latency bound. (5 workers)",
    },
    "go": {"lookup": "Quits on latency bound", "template": "Quits on latency bound"},
    "rust": {
        "lookup": "Quits on latency bound, hits max VUs around 3.75kreq/s",
        "template": "Quits on latency bound, hits max VUs around 3.5kreq/s",
    },
}

BUCKET_TIME = 1

all_stats_total = {}

ax = None

for endpoint in endpoints:
    all_stats = {}
    plt.clf()
    plt.rcParams["figure.figsize"] = [12, 3]
    used_languages = []
    for lang in languages:
        stats = {
            "rate": 0,
            "avg": 0,
            "med": 0,
            "p90": 0,
            "p95": 0,
        }
        
        if not os.path.exists(f"k6/data/{lang}-{endpoint}.csv") or not os.path.exists(f"k6/data/{lang}-{endpoint}-summary.json"):
            print(endpoint, lang, "Skipping due to missing files...")
            continue
        print(endpoint, lang, "Opening CSV file...")
        df = pd.read_csv(f"k6/data/{lang}-{endpoint}.csv")
        used_languages.append(lang)
        summary = {}
        print(endpoint, lang, "Opening summary file...")
        with open(f"k6/data/{lang}-{endpoint}-summary.json") as summary_file:
            summary = json.load(summary_file)

        print(endpoint, lang, "Gathering metrics...")
        metrics = summary["metrics"]

        duration = metrics["http_req_duration"]
        stats["avg"] = duration["values"]["avg"]
        stats["med"] = duration["values"]["med"]
        stats["p90"] = duration["values"]["p(90)"]
        stats["p95"] = duration["values"]["p(95)"]
        reqs = metrics["http_reqs"]

        for metric_name, metric in metrics.items():
            if (
                metric_name.startswith("http_reqs")
                or metric_name == "dropped_iterations"
            ):
                if metric["values"]["count"] > 0:
                    print(endpoint, lang, metric_name, metric["values"]["count"])

        print(endpoint, lang, "Processing points...")

        points = df[df["metric_name"] == "http_reqs"].reset_index()
        points["timestamp"] = points["timestamp"].astype("datetime64[s]")
        points["buckets"] = points["timestamp"].dt.floor(f"{BUCKET_TIME}s")
        data = points
        counter_data = data.groupby("buckets", dropna=False).agg(
            {"metric_value": "sum"}
        )
        counter_data["metric_value"] = counter_data["metric_value"].div(BUCKET_TIME)
        start_time = counter_data.index.min()
        #print(start_time, counter_data)

        counter_data = counter_data.rename(index=lambda v: v - start_time)
        #print(counter_data)

        if ax is None:
            ax = counter_data.plot(xlabel="Time", label=lang)
        else:
            counter_data.plot(xlabel="Time", label=lang, ax=ax)

        # plt.show()

        stats["rate"] = (
            counter_data.sort_values("metric_value", ascending=False)
            .head(5)["metric_value"]
            .mean()
        )

        all_stats[lang] = stats

    plt.legend(used_languages)
    plt.title("Requests per second")
    plt.savefig(f"graphs/requests-{endpoint}.svg", format="svg", bbox_inches="tight")

    all_stats_total[endpoint]=all_stats

for endpoint, all_stats in all_stats_total.items():
    print(f"\n\nTable for endpoint: {endpoint}\n")
    for lang, stats in all_stats.items():
        print(
            f"| {implementations[lang]} | {stats['rate']:5,.0f} | {stats['avg']:6,.1f} | {stats['med']:7,.1f} | {stats['p90']:6,.1f} | {stats['p95']:6,.1f} | {notes.get(lang,{}).get(endpoint,'')} |"
        )
