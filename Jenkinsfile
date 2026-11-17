pipeline {
    agent any

    stages {

        stage('Verify') {
            steps {
                echo 'Verifying project files'
                bat 'dir'
            }
        }

        stage('Setup Environment') {
            steps {
                echo 'Creating Python virtual environment'
                bat 'python -m venv .venv'

                echo 'Installing dependencies'
                bat '.venv\\Scripts\\python -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                echo 'Running FastAPI automated tests'
                bat '.venv\\Scripts\\python -m pytest -v'
            }
        }

        stage('Build') {
            steps {
                echo 'Application tests completed'
                bat '.venv\\Scripts\\python --version'
            }
        }

        stage('Docker Connectivity') {
            steps {
                echo 'Checking Docker CLI using its absolute path'

                bat '"C:\\Users\\MANOJ KUMAR SUNKARA\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" version'
            }
        }
    }
}
