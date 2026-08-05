pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }


        stage('Check Workspace') {
            steps {
                sh 'pwd && ls -la'
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