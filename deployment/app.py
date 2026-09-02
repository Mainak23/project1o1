import os
import logging
import numpy as np
import mlflow
from mlflow.tracking import MlflowClient
from fastapi import FastAPI, HTTPException


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MLFLOW_URI = os.environ["MLFLOW_TRACKING_URI"]

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "ml-training"
)

MODEL_ALIAS = os.getenv(
    "MODEL_ALIAS",
    "candidate"
)


# ---------------------------------------------------------
# MLflow configuration
# ---------------------------------------------------------

mlflow.set_tracking_uri(MLFLOW_URI)

client = MlflowClient(
    tracking_uri=MLFLOW_URI
)


# ---------------------------------------------------------
# Get model from MLflow Registry
# ---------------------------------------------------------

logger.info(
    "Looking for model '%s' with alias '%s'",
    MODEL_NAME,
    MODEL_ALIAS
)

model_version = client.get_model_version_by_alias(
    MODEL_NAME,
    MODEL_ALIAS
)

MODEL_URI = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"

logger.info(
    "Model found | name=%s | version=%s | run_id=%s",
    model_version.name,
    model_version.version,
    model_version.run_id
)

logger.info(
    "Model source: %s",
    model_version.source
)


# ---------------------------------------------------------
# Load model
# ---------------------------------------------------------

logger.info(
    "Loading model from MLflow: %s",
    MODEL_URI
)

model = mlflow.pyfunc.load_model(
    MODEL_URI
)

logger.info(
    "Model loaded successfully | name=%s | version=%s",
    MODEL_NAME,
    model_version.version
)


# ---------------------------------------------------------
# FastAPI
# ---------------------------------------------------------

app = FastAPI(
    title="ML Model Serving API",
    version="1.0"
)


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# Model information
# ---------------------------------------------------------

@app.get("/model")
def model_info():

    return {
        "model_name": model_version.name,
        "model_version": model_version.version,
        "model_alias": MODEL_ALIAS,
        "run_id": model_version.run_id
    }


# ---------------------------------------------------------
# Prediction
# ---------------------------------------------------------

@app.post("/predict")
def predict(request: dict):

    try:
        # JSON list -> NumPy array
        input_data = np.asarray(
            request["data"],
            dtype=np.float64
        )

        # Model expects (N, 30)
        if input_data.ndim != 2:
            raise ValueError(
                f"Expected 2D input (N, 30), got shape {input_data.shape}"
            )

        if input_data.shape[1] != 30:
            raise ValueError(
                f"Expected 30 features, got {input_data.shape[1]}"
            )

        prediction = model.predict(input_data)

        return {
            "prediction": prediction.tolist()
        }

    except Exception as exc:

        logger.exception("Prediction failed")

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc
