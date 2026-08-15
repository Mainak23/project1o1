import os
import logging
import mlflow
from mlflow.tracking import MlflowClient


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# MLflow
# --------------------------------------------------

MLFLOW_URI = os.environ["MLFLOW_TRACKING_URI"]

mlflow.set_tracking_uri(MLFLOW_URI)

client = MlflowClient()

MODEL_NAME = "ml-training"
PRIMARY_METRIC = "f1"


# --------------------------------------------------
# Find top 2 registered models
# --------------------------------------------------

def get_top_models():

    versions = client.search_model_versions(
        f"name='{MODEL_NAME}'"
    )

    candidates = []

    for version in versions:

        run_id = version.run_id

        if not run_id:
            continue

        run = client.get_run(run_id)

        metric = run.data.metrics.get(PRIMARY_METRIC)

        if metric is None:
            logger.warning(
                "Version %s has no metric '%s'",
                version.version,
                PRIMARY_METRIC
            )
            continue

        candidates.append({
            "version": version.version,
            "run_id": run_id,
            "metric": metric
        })

        logger.info(
            "Model | version=%s | run_id=%s | %s=%.4f",
            version.version,
            run_id,
            PRIMARY_METRIC,
            metric
        )

    if len(candidates) < 2:
        raise RuntimeError(
            "Need at least 2 valid registered model versions"
        )

    candidates.sort(
        key=lambda x: x["metric"],
        reverse=True
    )

    return candidates[:2]


# --------------------------------------------------
# Promote models
# --------------------------------------------------

def promote_models(top_models):

    champion = top_models[0]
    candidate = top_models[1]

    # Best model
    client.set_registered_model_alias(
        name=MODEL_NAME,
        alias="champion",
        version=champion["version"]
    )

    # Second-best model
    client.set_registered_model_alias(
        name=MODEL_NAME,
        alias="candidate",
        version=candidate["version"]
    )

    logger.info(
        "CHAMPION | version=%s | run_id=%s | f1=%.4f",
        champion["version"],
        champion["run_id"],
        champion["metric"]
    )

    logger.info(
        "CANDIDATE | version=%s | run_id=%s | f1=%.4f",
        candidate["version"],
        candidate["run_id"],
        candidate["metric"]
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    logger.info(
        "Starting model promotion | MLflow=%s",
        MLFLOW_URI
    )

    top_models = get_top_models()

    promote_models(top_models)

    logger.info("Model promotion completed")