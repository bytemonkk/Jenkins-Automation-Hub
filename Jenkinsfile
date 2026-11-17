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

                echo 'Installing project dependencies'

                bat '.venv\\Scripts\\python -m pip install -r requirements.txt'
            }
        }

        stage('Build') {
            steps {
                echo 'Python environment is ready'

                bat '.venv\\Scripts\\python --version'
            }
        }
    }
}
