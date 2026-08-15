import os
import logging
from turtle import pd
import mlflow
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


MLFLOW_URI=mlflow.set_tracking_uri(
    os.environ["MLFLOW_TRACKING_URI"]
)
git_commit = os.getenv("GIT_COMMIT", "unknown")


logger.info("Connecting to MLflow: %s", MLFLOW_URI)

experiments = mlflow.search_experiments()

logger.info("Found %d experiments", len(experiments))

results = []

for experiment in experiments:

    if experiment.lifecycle_stage != "active":
        continue

    logger.info(
        "Reading experiment: %s (ID=%s)",
        experiment.name,
        experiment.experiment_id
    )

    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="attributes.status = 'FINISHED'",
    )

    logger.info(
        "Found %d finished runs in %s",
        len(runs),
        experiment.name
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

if df.empty:
    logger.warning("No finished model runs found")
else:

    top_3 = (
        df
        .dropna(subset=["f1"])
        .sort_values("f1", ascending=False)
        .head(3)
    )

    logger.info("========== TOP 3 MODELS ==========")

    for rank, (_, model) in enumerate(top_3.iterrows(), start=1):

        logger.info(
            "#%d | Experiment=%s | Run ID=%s | F1=%.4f | Accuracy=%.4f",
            rank,
            model["experiment_name"],
            model["run_id"],
            model["f1"],
            model["accuracy"],
        )

    logger.info("==================================")