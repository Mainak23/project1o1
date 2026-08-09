pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm

                sh '''
                    echo "===== WORKSPACE ====="
                    pwd

                    echo "===== FILES ====="
                    ls -la

                    echo "===== ALL FILES ====="
                    find . -maxdepth 2 -type f | sort
                '''
            }
        }


        stage('Create Network') {
            steps {
                sh '''
                    podman network create ml-network || true
                '''
            }
        }

        stage('Build MLflow Server Image') {
            steps {
                sh '''
                    podman build \
                        --cgroup-manager=cgroupfs \
                        -t mlflow-server:latest \
                        -f Dockerfile.mlflow-server \
                        .
                '''
            }
        }

        stage('Run MLflow Server') {
            steps {
                sh '''
                    podman run --rm \
                        --name mlflow \
                        --network ml-network \
                        -p 5000:5000 \
                        -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                        -v $(pwd)/mlruns:/mlruns \
                        mlflow-server:latest
                '''
            }
        }

        stage('Wait for MLflow Server') {
            steps {
                sh '''
                    echo "Waiting for MLflow server to be ready..."
                    until curl -s http://localhost:5000/health | grep -q '"status":"healthy"'; do
                        echo "MLflow server is not ready yet. Waiting..."
                        sleep 5
                    done
                    echo "MLflow server is ready."
                '''
            }
        }
        stage('Run MLflow UI') {
            steps {
                sh '''
                    podman run --rm \
                        --name mlflow-ui \
                        --network ml-network \
                        -p 5001:5000 \
                        -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                        mlflow-server:latest
                '''
            }
        }
        stage('Wait for MLflow UI') {
            steps {
                sh '''
                    echo "Waiting for MLflow UI to be ready..."
                    until curl -s http://localhost:5001/ | grep -q 'MLflow Tracking'; do
                        echo "MLflow UI is not ready yet. Waiting..."
                        sleep 5
                    done
                    echo "MLflow UI is ready."
                '''
            }
        }
        stage('Build ML Training Image') {
            steps {
                sh '''
                    podman build \
                        --cgroup-manager=cgroupfs \
                        -t ml-training:${BUILD_NUMBER} \
                        -f Dockerfile.ml-training \
                        .
                '''
            }
        }

        stage('Train') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'mlflow-tracking-uri',
                        variable: 'MLFLOW_TRACKING_URI'
                    )
                ]) {
                    sh '''
                        podman run --rm \
                        --network ml-network \
                        -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                        ml-training:${BUILD_NUMBER}
                    '''
                }
            }
        }
    }
}