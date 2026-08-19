pipeline {
    agent any

    environment {
        MLFLOW_TRACKING_URI = 'http://mlflow:5000'
        GIT_PYTHON_REFRESH = 'quiet'
        XDG_RUNTIME_DIR = '/run/user/111'
        PATH = "/var/lib/jenkins/bin:${env.PATH}"
    }

    stages {

        // --------------------------------------------------
        // 1. Checkout source code
        // --------------------------------------------------
        stage('Checkout') {
            steps {
                checkout scm

                sh '''
                    echo "===== WORKSPACE ====="
                    pwd

                    echo "===== FILES ====="
                    find . -maxdepth 3 -type f | sort

                    echo "===== GIT INFORMATION ====="
                    echo "GIT_COMMIT=${GIT_COMMIT}"
                    git rev-parse HEAD
                '''
            }
        }


        // --------------------------------------------------
        // 2. Verify project structure
        // --------------------------------------------------
        stage('Verify Project') {
            steps {
                sh '''
                    echo "===== Training / Registration ====="
                    ls -lah register

                    echo "===== Deployment / Serving ====="
                    ls -lah deployment
                '''
            }
        }


        // --------------------------------------------------
        // 3. Build training image
        // --------------------------------------------------
        stage('Build ML Training Image') {
            steps {
                sh '''
                    podman build \
                        -t ml-training:${BUILD_NUMBER} \
                        ./register
                '''
            }
        }


        // --------------------------------------------------
        // 4. Register model in MLflow
        // --------------------------------------------------
        stage('Register Model') {
            steps {
                sh '''
                    podman run --rm \
                        --network ml-network \
                        -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                        -e MLFLOW_S3_ENDPOINT_URL=http://minio:9000 \
                        -e AWS_ACCESS_KEY_ID=minioadmin \
                        -e AWS_SECRET_ACCESS_KEY=minioadmin123 \
                        -e GIT_COMMIT="${GIT_COMMIT}" \
                        ml-training:${BUILD_NUMBER}
                '''
            }
        }


        // --------------------------------------------------
        // 5. Build serving image
        // --------------------------------------------------
        stage('Build ML Serving Image') {
            steps {
                sh '''
                    podman build \
            -t ghcr.io/mainak23/ml-serving:${BUILD_NUMBER} \
            ./deployment

            podman push \
            ghcr.io/mainak23/ml-serving:${BUILD_NUMBER}
                '''
            }
        }

      


        // --------------------------------------------------
        // 6. Test serving image locally
        // --------------------------------------------------
        stage('Test Serving Image') {
            steps {
                sh '''
                    podman run -d \
                        --name ml-serving-test-${BUILD_NUMBER} \
                        --network ml-network \
                        -p 8083:8080 \
                        -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
                        -e MLFLOW_S3_ENDPOINT_URL=http://minio:9000 \
                        -e AWS_ACCESS_KEY_ID=minioadmin \
                        -e AWS_SECRET_ACCESS_KEY=minioadmin123 \
                        ml-serving:${BUILD_NUMBER}

                    sleep 10

                    curl -f http://localhost:8083/health

                    podman stop ml-serving-test-${BUILD_NUMBER}
                    podman rm ml-serving-test-${BUILD_NUMBER}
                '''
            }
        }


        // --------------------------------------------------
        // 7. Show built images
        // --------------------------------------------------
        stage('Verify Images') {
            steps {
                sh '''
                    podman images | grep -E 'ml-training|ml-serving'
                '''
            }
        }


        // --------------------------------------------------
        // 8. Clean workspace
        // --------------------------------------------------
        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }
    }
}