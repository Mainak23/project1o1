pipeline {
    agent any

    environment {
        MLFLOW_TRACKING_URI = 'http://mlflow:5000'
        GIT_PYTHON_REFRESH = 'quiet'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm

                sh '''
                    echo "===== WORKSPACE ====="
                    pwd
                    ls -la
                    find . -maxdepth 2 -type f | sort

                    echo "===== GIT INFORMATION ====="
                    echo "GIT_COMMIT=${GIT_COMMIT}"
                    git rev-parse HEAD
                    
                '''
            }
        }

        stage('Build ML Training Image') {
            steps {
                sh '''
                    podman build \
                        -t ml-training:${BUILD_NUMBER} \
                        .
                '''
            }
        }

        stage('Train') {
            steps {
                sh '''
                    podman run --rm \
                        --network ml-network \
                        -e MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI}" \
                        -e GIT_COMMIT="${GIT_COMMIT}" \
                        -e GIT_PYTHON_REFRESH="${GIT_PYTHON_REFRESH}" \
                        ml-training:${BUILD_NUMBER}
                '''
            }
        }
    }
}