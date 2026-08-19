import os
import logging
import mlflow
from mlflow.tracking import MlflowClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

MLFLOW_URI = os.environ["MLFLOW_TRACKING_URI"]
mlflow.set_tracking_uri(MLFLOW_URI)

client = MlflowClient()

MODEL_NAME = "ml-training"


def promote_models():

    versions = client.search_model_versions(
        f"name='{MODEL_NAME}'"
    )

    if len(versions) < 2:
        raise RuntimeError(
            "At least 2 registered model versions are required"
        )

    # Convert to list and sort by version number
    versions = sorted(
        versions,
        key=lambda x: int(x.version),
        reverse=True
    )

    champion = versions[0]
    candidate = versions[1]

    logger.info(
        "Champion | version=%s | run_id=%s",
        champion.version,
        champion.run_id
    )

    logger.info(
        "Candidate | version=%s | run_id=%s",
        candidate.version,
        candidate.run_id
    )

    # Promote best/latest version
    client.set_registered_model_alias(
        name=MODEL_NAME,
        alias="champion",
        version=champion.version
    )

    # Promote second version
    client.set_registered_model_alias(
        name=MODEL_NAME,
        alias="candidate",
        version=candidate.version
    )

    logger.info(
        "Version %s promoted as champion",
        champion.version
    )

    logger.info(
        "Version %s promoted as candidate",
        candidate.version
    )


if __name__ == "__main__":

    logger.info(
        "Starting model promotion | MLflow=%s",
        MLFLOW_URI
    )

    promote_models()

    logger.info("Model promotion completed")