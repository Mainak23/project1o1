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
        stage('Register Image') {
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

        stage('Build and Push Serving Image') {
            steps {
                withCredentials([
                        usernamePassword(
                            credentialsId: '98484553-4b67-41bb-b338-ca81a9d99213',
                            usernameVariable: 'USER',
                            passwordVariable: 'PASSWORD'
                        )
                    ])
                { sh '''
                        podman build \
                            -t ghcr.io/mainak23/ml-serving:${BUILD_NUMBER} \
                            ./deployment


                        podman login ghcr.io
                        
                        podman push \
                            ghcr.io/mainak23/ml-serving:${BUILD_NUMBER}
                    '''
            }
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

        stage('Push Manifest') {
            steps {
                   withCredentials([
                        usernamePassword(
                            credentialsId: '98484553-4b67-41bb-b338-ca81a9d99213',
                            usernameVariable: 'USER',
                            passwordVariable: 'PASSWORD'
                        )
                    ])
                {
                    sh '''

                    printf "%s" "$PASSWORD" | podman login ghcr.io \
                            -u "$USER" \
                            --password-stdin

                    git clone https://github.com/Mainak23/deployment.git deployment-repo

                    cd deployment-repo

                    # Copy/update your manifest
                    cp model-deployment.yaml deployment-repo/model-deployment.yaml

                    git config user.name "Mainak23"
                    git config user.email "mainakray111@gmail.com"

                    git add model-deployment.yaml
                    git commit -m "Deploy ml-serving ${BUILD_NUMBER}" || true
                    git push origin main
                '''
            }
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
