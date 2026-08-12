pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm

                sh '''
                    echo "===== WORKSPACE ====="
                    pwd
                    ls -la
                    find . -maxdepth 2 -type f | sort
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
                        -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                        ml-training:${BUILD_NUMBER}
                '''
            }
        }
    }
}