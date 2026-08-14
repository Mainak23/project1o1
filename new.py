import mlflow
import pandas as pd


MLFLOW_URI = "http://localhost:5000"

mlflow.set_tracking_uri(MLFLOW_URI)


# Get all experiments
experiments = mlflow.search_experiments()

results = []

for experiment in experiments:

    # Skip deleted experiments
    if experiment.lifecycle_stage != "active":
        continue

    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="attributes.status = 'FINISHED'",
    )

    if runs.empty:
        continue

    for _, run in runs.iterrows():

        results.append({
            "experiment_name": experiment.name,
            "experiment_id": experiment.experiment_id,
            "run_id": run["run_id"],
            "status": run["status"],
            "start_time": run["start_time"],
            "accuracy": run.get("metrics.accuracy"),
            "f1": run.get("metrics.f1"),
            "precision": run.get("metrics.precision"),
            "recall": run.get("metrics.recall"),
            "artifact_uri": run["artifact_uri"],
        })


df = pd.DataFrame(results)


# Example ranking: highest F1
top_3 = (
    df
    .dropna(subset=["f1"])
    .sort_values("f1", ascending=False)
    .head(3)
)


print("\n===== TOP 3 MODELS =====\n")

print(
    top_3[
        [
            "experiment_name",
            "run_id",
            "f1",
            "accuracy",
            "precision",
            "recall",
            "artifact_uri",
        ]
    ].to_string(index=False)
)
