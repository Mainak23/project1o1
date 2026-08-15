
# ============================================================
# MLFLOW TRAINING BOILERPLATE
# ============================================================

from mlflow.models.signature import infer_signature
import os

import mlflow
import mlflow.sklearn

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
#ok
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    log_loss
)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# 1. TRACKING SERVER
# ============================================================

mlflow.set_tracking_uri(
    os.environ["MLFLOW_TRACKING_URI"]
)
git_commit = os.getenv("GIT_COMMIT", "unknown")


# ============================================================
# 2. EXPERIMENT
# ============================================================

EXPERIMENT_NAME = "minio-test"

mlflow.set_experiment(
    EXPERIMENT_NAME
)

experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)

if experiment is None:
    experiment_id = mlflow.create_experiment(EXPERIMENT_NAME)
else:
    experiment_id = experiment.experiment_id

#jnmmn

mlflow.set_experiment(EXPERIMENT_NAME)

# ============================================================
# 3. DATA
# ============================================================

data = load_breast_cancer()

X = data.data
y = data.target

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# 4. MODEL CONFIGURATION
# ============================================================

C = 9
MAX_ITER = 10
SOLVER = "liblinear"
PENALTY = "l1"


# ============================================================
# 5. MODEL
# ============================================================

model = Pipeline([
    ("scaler", StandardScaler()),

    ("classifier", LogisticRegression(
        C=C,
        max_iter=MAX_ITER,
        solver=SOLVER,
        penalty=PENALTY
    ))
])


# ============================================================
# 6. START RUN
# ============================================================

with mlflow.start_run(
    run_name="Logistic Regression Baseline-80"
) as run:
    mlflow.set_tag("git_commit", git_commit)

    # --------------------------------------------------------
    # ATTRIBUTES
    # --------------------------------------------------------
    # MLflow automatically creates:
    #
    # run_id
    # run_name
    # start_time
    # end_time
    # status
    #
    # We normally DON'T log these ourselves.


    # --------------------------------------------------------
    # PARAMETERS
    # --------------------------------------------------------
    # "What configuration did I use?"

    mlflow.log_params({

        "model": "LogisticRegression",

        "C": C,

        "max_iter": MAX_ITER,

        "solver": SOLVER,

        "penalty": PENALTY,

        "test_size": 0.20,

        "random_state": 42,

        "train_samples": len(X_train),

        "test_samples": len(X_test),

        "features": X.shape[1]
    })


    # --------------------------------------------------------
    # TAGS
    # --------------------------------------------------------
    # "What context describes this run?"

    mlflow.set_tags({

        "algorithm": "logistic_regression",

        "task": "binary_classification",

        "environment": "development",

        "dataset": "breast_cancer",

        "team": "data_science",

        "version": "v10"
    })


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    model.fit(
        X_train,
        y_train
    )


    # --------------------------------------------------------
    # PREDICT
    # --------------------------------------------------------

    y_pred = model.predict(
        X_test
    )

    y_prob = model.predict_proba(
        X_test
    )[:, 1]


    # --------------------------------------------------------
    # EVALUATE
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred
    )

    recall = recall_score(
        y_test,
        y_pred
    )

    f1 = f1_score(
        y_test,
        y_pred
    )

    roc_auc = roc_auc_score(
        y_test,
        y_prob
    )

    loss = log_loss(
        y_test,
        y_prob
    )


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------
    # "What performance did I get?"

    mlflow.log_metrics({

        "accuracy": accuracy,

        "precision": precision,

        "recall": recall,

        "f1_score": f1,

        "roc_auc": roc_auc,

        "log_loss": loss
    })


    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------
    # "What model was produced?"
    #This only logs the model as an artifact/model output of the run.

    # infer model signature (inputs/outputs) for reproducibility
    signature = infer_signature(X_train, model.predict(X_train))

    logged_model = mlflow.sklearn.log_model(
        model,
        name="model",
        signature=signature
    )

    logger.info(
    f"model_id={logged_model.model_id}, "
    f"run_id={logged_model.run_id}, "
    f"model_uri={logged_model.model_uri}"
)
    # --------------------------------------------------------
    # RUN INFORMATION
    # --------------------------------------------------------

    print(
        "Run ID:",
        run.info.run_id
    )

    print(
        "Experiment ID:",
        run.info.experiment_id
    )

    print(
        "Accuracy:",
        accuracy
    )

    print(
        "F1:",
        f1
    )

