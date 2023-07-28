import json
import pandas as pd

languages = [
    "dotnet",
    "rust",
    "php",
    "python",
    "go"
]

BUCKET_TIME = 1

all_stats = {}

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
    duration = summary['metrics']['http_req_duration']
    stats["avg"] = duration['values']['avg']
    stats["med"] = duration['values']['med']
    stats["p90"] = duration['values']['p(90)']
    stats["p95"] = duration['values']['p(95)']
    reqs = summary['metrics']['http_reqs']
    print(lang, "Gathering metrics...")
    metrics = summary['metrics']

    print(lang, "Processing points...")

    points = df[df['metric_name']=="http_reqs"].reset_index()
    points['timestamp'] = points['timestamp'].astype('datetime64[s]')
    points['buckets'] = points['timestamp'].dt.floor(f'{BUCKET_TIME}s')
    data = points

    counter_data = data.groupby("buckets", dropna=False).agg({'metric_value':'sum'})
    counter_data["metric_value"] = counter_data["metric_value"].div(BUCKET_TIME)
    stats["rate"] = counter_data.sort_values('metric_value',ascending = False).head(5)['metric_value'].mean()

    all_stats[lang] = stats
    
for lang, stats in all_stats.items():
    print(f"| {stats['rate']:5,.0f} | {stats['avg']:6,.1f} | {stats['med']:6,.1f} | {stats['p90']:6,.1f} | {stats['p95']:6,.1f} |")