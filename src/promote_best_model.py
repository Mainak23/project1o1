import logging
import os
import mlflow
from mlflow import MlflowClient


# --------------------------------------------------
# Configuration
# --------------------------------------------------

MLFLOW_URI=mlflow.set_tracking_uri(
    os.environ["MLFLOW_TRACKING_URI"]
)
MODEL_NAME = "ml-training"

PRIMARY_METRIC = "f1"

# Compare only these registered versions
CANDIDATE_VERSIONS = [1, 2, 3]


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

mlflow.set_tracking_uri(MLFLOW_URI)

client = MlflowClient()


def get_best_model():

    candidates = []

    for version_number in CANDIDATE_VERSIONS:

        version = client.get_model_version(
            name=MODEL_NAME,
            version=str(version_number)
        )

        run_id = version.run_id

        run = client.get_run(run_id)

        metric_value = run.data.metrics.get(PRIMARY_METRIC)

        if metric_value is None:
            logger.warning(
                "Version %s has no metric '%s'",
                version_number,
                PRIMARY_METRIC
            )
            continue

        candidates.append({
            "version": version_number,
            "run_id": run_id,
            "metric": metric_value
        })

        logger.info(
            "Candidate | version=%s | run_id=%s | %s=%.4f",
            version_number,
            run_id,
            PRIMARY_METRIC,
            metric_value
        )

    if not candidates:
        raise RuntimeError("No valid model candidates found")

    best = max(
        candidates,
        key=lambda x: x["metric"]
    )

    return best


def promote_model(best):

    version = str(best["version"])

    logger.info(
        "Best model: version=%s | run_id=%s | %s=%.4f",
        version,
        best["run_id"],
        PRIMARY_METRIC,
        best["metric"]
    )

    client.set_registered_model_alias(
        name=MODEL_NAME,
        alias="champion",
        version=version
    )

    logger.info(
        "Model version %s promoted as 'champion'",
        version
    )


if __name__ == "__main__":

    logger.info("Starting model promotion")

    best_model = get_best_model()

    promote_model(best_model)

    logger.info("Model promotion completed")