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
    print(response.status_code, response.text)
    # ---------------------------------------------
    # API should succeed
    # ---------------------------------------------

    assert response.status_code == 200, response.text

    # ---------------------------------------------
    # Read prediction
    # ---------------------------------------------

    body = response.json()

    #assert "prediction" in body

    prediction = body

    # ---------------------------------------------
    # Verify prediction structure
    # ---------------------------------------------

    assert isinstance(prediction, dict)

    assert len(prediction) == 1

    # ---------------------------------------------
    # Prediction must be a valid breast-cancer class
    # ---------------------------------------------

    assert prediction

    #pytest -v test_ml_serving.py

# curl -X POST "http://127.0.0.1:8081/predict" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "data": [[17.99,10.38,122.8,1001.0,0.1184,0.2776,0.3001,0.1471,0.2419,0.07871,1.095,0.9053,8.589,153.4,0.006399,0.04904,0.05373,0.01587,0.03003,0.006193,25.38,17.33,184.6,2019.0,0.1622,0.6656,0.7119,0.2654,0.4601,0.1189]]
#   }'

