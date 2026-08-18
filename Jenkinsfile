pipeline {
    agent any

    environment {
        MLFLOW_TRACKING_URI = 'http://mlflow:5000'
        GIT_PYTHON_REFRESH = 'quiet'
        XDG_RUNTIME_DIR = '/run/user/111'
        PATH = "/var/lib/jenkins/bin:${env.PATH}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm

                sh '''
                    echo "===== WORKSPACE new ====="
                    pwd
                    
                    echo "training files:"
                    
                    find . -maxdepth 2 -type f | sort

                    echo "===== GIT INFORMATION ====="
                    echo "GIT_COMMIT=${GIT_COMMIT}"
                    git rev-parse HEAD
                    
                '''
            }
        }

        stage('Build ML Register Image') {
            steps {
                
                sh '''
                    podman build \
                    -t ml-training:${BUILD_NUMBER} \
                    ./training
                '''
                }
           
        }

        // stage('Trivy Scan') {
        //     steps {
        //         sh '''
        //          rm -f ml-training.tar

        //     podman save \
        //         --format docker-archive \
        //         -o ml-training.tar \
        //         "localhost/ml-training:${BUILD_NUMBER}"

        //     podman run --rm \
        //         -v "$PWD/ml-training.tar:/scan/ml-training.tar:ro" \
        //         -v trivy-cache:/root/.cache/trivy \
        //         docker.io/aquasec/trivy:0.72.0 \
        //         image \
        //         --input /scan/ml-training.tar \
        //         --severity HIGH,CRITICAL \
        //         --format table
               
        // '''
                
        //     }
        // }

        stage('Register model') {
            steps {
                sh '''
                    podman run --rm \
                --network ml-network \
                -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                -e MLFLOW_S3_ENDPOINT_URL=http://minio:9000\
                -e AWS_ACCESS_KEY_ID=minioadmin \
                -e AWS_SECRET_ACCESS_KEY=minioadmin123 \
                -e GIT_COMMIT="${GIT_COMMIT}"\
                ml-training:${BUILD_NUMBER}
                '''
            }
        }

        stage('Build and push serving image') {
            steps {
                sh '''
                    podman build \
                    -t ml-serving:${BUILD_NUMBER} \
                    ./serving
                '''
            }
        }
        stage('Deploy model') {
            steps {
                sh '''
                    podman run --rm \
                --network ml-network \
                -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                -e MLFLOW_S3_ENDPOINT_URL=http://minio:9000\
                -e AWS_ACCESS_KEY_ID=minioadmin \
                -e AWS_SECRET_ACCESS_KEY=minioadmin123 \
                -e GIT_COMMIT="${GIT_COMMIT}"\
                ml-serving:${BUILD_NUMBER}
                '''
            }
        }
    }
}