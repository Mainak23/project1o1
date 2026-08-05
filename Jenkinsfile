pipeline {
    agent any

    stages {

        stage('Check Workspace') {
            steps {
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
                        -t ml-training:${BUILD_NUMBER} \
                        .
                '''
            }
        }

        stage('Train') {
            steps {
                sh '''
                    podman run --rm \
                        ml-training:${BUILD_NUMBER}
                '''
            }
        }
    }
}