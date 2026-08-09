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

        stage('Create Network') {
            steps {
                sh '''
                    podman network create ml-network || true
                '''
            }
        }

        stage('Build MLflow Image') {
            steps {
                sh '''
                    podman build \
                        --cgroup-manager=cgroupfs \
                        -t mlflow-server:latest \
                        -f Dockerfile.mlflow\
                        .
                '''
            }
        }

        stage('Run MLflow') {
            steps {
                sh '''
                    podman rm -f mlflow 2>/dev/null || true

                    podman run -d \
                    --name mlflow \
                    --network ml-network \
                    -p 5000:5000 \
                    mlflow-server:latest
                    '''
            }
        }


        stage('Wait for MLflow') {
            steps {
                sh '''
                    echo "Waiting for MLflow..."

                    until curl -sf 127.0.0.1:5000/health > /dev/null; do
                        echo "MLflow not ready..."
                        sleep 5
                    done

                    echo "MLflow is ready."
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

        stage('Build ML Training Image') {
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
                echo "Cleaning MLflow container..."
                podman rm -f mlflow 2>/dev/null || true
            '''
        }
    }
}