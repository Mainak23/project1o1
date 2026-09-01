import requests
from sklearn.datasets import load_breast_cancer

BASE_URL = "http://localhost:8081"


def test_health():

    response = requests.get(
        f"{BASE_URL}/health"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"


def test_model_info():

    response = requests.get(
        f"{BASE_URL}/model"
    )

    assert response.status_code == 200

    body = response.json()

    assert "model_name" in body
    assert "model_version" in body
    assert "model_alias" in body
    assert "run_id" in body


def test_breast_cancer_prediction():

    # ---------------------------------------------
    # Load same dataset used for training
    # ---------------------------------------------

    data = load_breast_cancer()

    X = data.data
    y = data.target

    # ---------------------------------------------
    # Select one sample
    # ---------------------------------------------

    sample = X[0]

    expected = y[0]

    # ---------------------------------------------
    # Verify input
    # ---------------------------------------------

    assert sample.shape == (30,)

    # ---------------------------------------------
    # API expects:
    #
    # {
    #     "data": [
    #         [30 features]
    #     ]
    # }
    # ---------------------------------------------

    payload = {
        "data": [
            sample.tolist()
        ]
    }

    # ---------------------------------------------
    # Call API
    # ---------------------------------------------

    response = requests.post(
        f"{BASE_URL}/predict",
        json=payload
    )

    # ---------------------------------------------
    # API should succeed
    # ---------------------------------------------

    assert response.status_code == 200, response.text

    # ---------------------------------------------
    # Read prediction
    # ---------------------------------------------

    body = response.json()

    assert "prediction" in body

    prediction = body["prediction"]

    # ---------------------------------------------
    # Verify prediction structure
    # ---------------------------------------------

    assert isinstance(prediction, list)

    assert len(prediction) == 1

    # ---------------------------------------------
    # Prediction must be a valid breast-cancer class
    # ---------------------------------------------

    assert prediction[0] in [0, 1]