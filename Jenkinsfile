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
        stage('Podman Diagnostics') {
        steps {
            sh '''
                echo "===== USER ====="
                whoami
                id

                echo "===== PODMAN ====="
                podman info

                echo "===== NETWORKS ====="
                podman network ls

                echo "===== ML NETWORK ====="
                podman network inspect ml-network || true
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
                    podman rm -f mlflow 2>/dev/null || true

                    podman run -d \
                        --name mlflow \
                        --network ml-network \
                        -p 5000:5000 \
                        -v "$(pwd)/mlruns:/mlruns" \
                        mlflow-server:latest
                '''
            }
        }

        stage('Wait for MLflow Server') {
            steps {
                sh '''
                    echo "Waiting for MLflow..."

                    until curl -s http://127.0.0.1:5000/health | grep -q '"status":"healthy"'; do
                        echo "MLflow is not ready..."
                        sleep 5
                    done

                    echo "MLflow is ready."
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

        stage('Test MLflow Network') {
            steps {
                sh '''
                    podman run --rm \
                        --network ml-network \
                        docker.io/curlimages/curl \
                        -v http://mlflow:5000
                '''
            }
        }

        stage('Train') {
            steps {
                sh '''
                    podman run --rm \
                        --network ml-network \
                        -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                        ml-training:${BUILD_NUMBER}
                '''
            }
        }
    }

    post {
        always {
            sh '''
                podman rm -f mlflow 2>/dev/null || true
            '''
        }
    }
}