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
                    echo "===== WORKSPACE new ====="
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

        stage('Trivy Scan') {
            steps {
                sh '''
                   podman run --rm \
                    -v "$XDG_RUNTIME_DIR/podman/podman.sock:/podman/podman.sock" \
                    -v trivy-cache:/root/.cache \
                    docker.io/aquasec/trivy:0.72.0 \
                    image \
                    --image-src podman \
                    --podman-host unix:///run/podman/podman.sock \
                    ml-training:105
                '''
            }
        }

        stage('Train') {
            steps {
                sh '''
                    podman run --rm \
                --network ml-network \
                -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                -e MLFLOW_S3_ENDPOINT_URL=http://minio:9000 \
                -e AWS_ACCESS_KEY_ID=minioadmin \
                -e AWS_SECRET_ACCESS_KEY=minioadmin123 \
                -e GIT_COMMIT="${GIT_COMMIT}"\
                ml-training:${BUILD_NUMBER}
                '''
            }
        }
    }
}