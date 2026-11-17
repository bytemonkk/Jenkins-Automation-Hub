
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code'
                checkout scm
            }
        }

        stage('Verify') {
            steps {
                echo 'Verifying project files'
                bat 'dir'
            }
        }

        stage('Build') {
            steps {
                echo 'Preparing FastAPI application'
                bat 'python --version'
            }
        }
    }
}
