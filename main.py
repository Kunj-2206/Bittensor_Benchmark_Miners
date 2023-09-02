import os
import json
import pandas as pd
from run_metrics import run_all_metric
import sys


question_per_metric = 1000
datetime_folder = run_all_metric(question_per_metric)

if datetime_folder == "Exception":
    sys.exit()

benchmark_folder = f'benchmark/{datetime_folder}/'
result_folder = f"results/{datetime_folder}/"
json_metrics_files = os.listdir(result_folder)

common_uids = None

for json_metrics_file in json_metrics_files:
    json_metric = json.load(open(result_folder+json_metrics_file))
    if common_uids is None:
        common_uids = set(json_metric.keys())

    else:
        common_uids = common_uids.intersection(set(json_metric.keys()))

columns = ['arc', 'boolq', 'mmlu', 'openbookqa', 'piqa', 'race', 'siqa', 'winogrande']
metrics_df = pd.DataFrame(columns=['UIDs'])
metrics_df['UIDs'] = list(common_uids)
metrics_df.set_index('UIDs', inplace=True)
for column in columns:
    metrics_df[column] = 0
accuracy_data = {}

for json_metrics_file in json_metrics_files:
    json_metric = json.load(open(result_folder+json_metrics_file))
    column_name = (json_metrics_file.split("_Miner_Metrics")[0]).lower()
    
    accuracy_scores = {uid: value["accuracy"] / 1000 for uid, value in json_metric.items() if uid in common_uids}
    
    accuracy_data[column_name] = accuracy_scores

for index, row in metrics_df.iterrows():
    uid = index
    for column_name, accuracy_scores in accuracy_data.items():
        metrics_df.loc[uid, column_name] = accuracy_scores.get(uid, 0)

metrics_df['average'] = metrics_df[columns].sum(axis=1) / len(columns) * 100
metrics_df['average'] = metrics_df['average'].round(2).astype(str) + '%'

csv_file = 'miner_benchmark.csv'
metrics_df.to_csv(os.path.join(benchmark_folder, csv_file))
print(metrics_df)

