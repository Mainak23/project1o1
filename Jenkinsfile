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

        stage('Build Training Image') {
            steps {
                sh '''
                    podman build \
                        --cgroup-manager=cgroupfs \
                        -t ml-training:${BUILD_NUMBER} \
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