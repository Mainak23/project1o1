import logging
import os
import mlflow
from mlflow.tracking import MlflowClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

MLFLOW_URI=mlflow.set_tracking_uri(
    os.environ["MLFLOW_TRACKING_URI"]
)
MODEL_NAME = "ml-training"



client = MlflowClient()


# Top 3 runs selected by your previous script
TOP_RUN_IDS = [
    "run_id_1",
    "run_id_2",
    "run_id_3",
]


def register_models():
    logger.info("Connecting to MLflow: %s", MLFLOW_URI)

    for rank, run_id in enumerate(TOP_RUN_IDS, start=1):

        model_uri = f"runs:/{run_id}/model"

        logger.info(
            "Registering #%d model | run_id=%s | uri=%s",
            rank,
            run_id,
            model_uri
        )

        try:
            result = mlflow.register_model(
                model_uri=model_uri,
                name=MODEL_NAME
            )

            logger.info(
                "Registered successfully | run_id=%s | version=%s",
                run_id,
                result.version
            )

        except Exception:
            logger.exception(
                "Failed to register model | run_id=%s",
                run_id
            )


if __name__ == "__main__":
    register_models()