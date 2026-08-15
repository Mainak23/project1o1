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
EXPERIMENT_NAME = "ml-training"


def get_top_runs():

    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)

    if experiment is None:
        raise Exception(f"Experiment not found: {EXPERIMENT_NAME}")

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="attributes.status = 'FINISHED'",
        order_by=["metrics.accuracy DESC"],
        max_results=3
    )

    return runs


def register_models():

    top_runs = get_top_runs()

    logger.info("Found %d top runs", len(top_runs))

    for rank, run in enumerate(top_runs, start=1):

        run_id = run.info.run_id
        accuracy = run.data.metrics.get("accuracy")

        model_uri = f"runs:/{run_id}/model"

        logger.info(
            "Registering #%d | run_id=%s | accuracy=%s",
            rank,
            run_id,
            accuracy
        )

        try:

            result = mlflow.register_model(
                model_uri=model_uri,
                name=MODEL_NAME
            )

            logger.info(
                "SUCCESS | run_id=%s | version=%s",
                run_id,
                result.version
            )

        except Exception:

            logger.exception(
                "FAILED | run_id=%s",
                run_id
            )


if __name__ == "__main__":
    register_models()