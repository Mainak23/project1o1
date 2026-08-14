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
                   trivy image \
                --severity HIGH,CRITICAL \
                --exit-code 1 \
                --cache-dir $HOME/.cache/trivy \
                "localhost/ml-training:${BUILD_NUMBER}"
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