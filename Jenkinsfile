pipeline {
    agent any

    environment {
        MLFLOW_TRACKING_URI = 'http://mlflow:5000'
        GIT_PYTHON_REFRESH = 'quiet'
         XDG_RUNTIME_DIR = '/run/user/111'
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
                   echo "USER=$(whoami)"
                    echo "UID=$(id -u)"
                    echo "XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"
                    ls -l "$XDG_RUNTIME_DIR/podman/podman.sock"

                    podman run --rm \
                        --userns=keep-id \
                        -v "$XDG_RUNTIME_DIR/podman/podman.sock:$XDG_RUNTIME_DIR/podman/podman.sock"  \
                        -v trivy-cache:/home/jenkins/.cache \
                        docker.io/aquasec/trivy:0.72.0 \
                        image \
                        --image-src podman \
                        --podman-host unix:///podman/podman.sock \
                        --cache-dir /home/jenkins/.cache/trivy \
                        --severity HIGH,CRITICAL \
                        --exit-code 1 \
                        localhost/ml-training:${BUILD_NUMBER}
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