import json
import pandas as pd

import matplotlib.pyplot as plt

languages = [
    "php",
    "python",
    "dotnet",
    "go",
    "go-fiber",
    "rust",
]

BUCKET_TIME = 1

all_stats = {}

plt.rcParams['figure.figsize'] = [12, 3]

ax = None

for lang in languages:
    stats = {
        "rate": 0,
        "avg": 0,
        "med":0,
        "p90":0,
        "p95":0,
    }
    print(lang, "Opening CSV file...")
    df = pd.read_csv(f"k6/data/{lang}.csv")
    
    summary = {}
    print(lang, "Opening summary file...")
    with open(f"k6/data/{lang}-summary.json") as summary_file:
        summary = json.load(summary_file)
    
    print(lang, "Gathering metrics...")
    metrics = summary['metrics']

    duration = metrics['http_req_duration']
    stats["avg"] = duration['values']['avg']
    stats["med"] = duration['values']['med']
    stats["p90"] = duration['values']['p(90)']
    stats["p95"] = duration['values']['p(95)']
    reqs = metrics['http_reqs']

    for metric_name, metric in metrics.items():
        if metric_name.startswith("http_reqs") or metric_name == "dropped_iterations":
            if metric['values']['count'] > 0:
                print(lang,metric_name, metric['values']['count'])

    print(lang, "Processing points...")

    points = df[df['metric_name']=="http_reqs"].reset_index()
    points['timestamp'] = points['timestamp'].astype('datetime64[s]')
    points['buckets'] = points['timestamp'].dt.floor(f'{BUCKET_TIME}s')
    data = points
    counter_data = data.groupby("buckets", dropna=False).agg({'metric_value':'sum'})
    counter_data["metric_value"] = counter_data["metric_value"].div(BUCKET_TIME)
    start_time = counter_data.index.min()
    print(start_time, counter_data)

    counter_data = counter_data.rename(index=lambda v : v - start_time)
    print(counter_data)

    if ax is None:
        ax = counter_data.plot(xlabel="Time", label=lang)
    else:
        counter_data.plot(xlabel="Time", label=lang, ax=ax)
    
    #plt.show()

    stats["rate"] = counter_data.sort_values('metric_value',ascending = False).head(5)['metric_value'].mean()

    all_stats[lang] = stats

plt.legend(languages)
plt.title("Requests per second")
plt.savefig("graphs/requests.svg", format="svg", bbox_inches='tight')
    
for lang, stats in all_stats.items():
    print(f"| {stats['rate']:5,.0f} | {stats['avg']:6,.1f} | {stats['med']:7,.1f} | {stats['p90']:6,.1f} | {stats['p95']:6,.1f} |")