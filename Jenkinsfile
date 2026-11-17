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

        stage('Docker Build') {
            steps {
                echo 'Building FastAPI Docker image'

                bat '"C:\\Users\\MANOJ KUMAR SUNKARA\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" build -t jenkins-automation-hub:latest .'
            }
        }
        
        stage('Docker Deploy') {
            steps {
                echo 'Removing previous application container if it exists'

                script {
                    def removeStatus = bat(
                        returnStatus: true,
                        script: '"C:\\Users\\MANOJ KUMAR SUNKARA\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" rm -f jenkins-automation-hub-app'
                    )

                    if (removeStatus != 0) {
                        echo 'No previous container found. Continuing with deployment.'
                    }
                }

                echo 'Starting updated FastAPI container'

                bat '"C:\\Users\\MANOJ KUMAR SUNKARA\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" run -d --restart unless-stopped --name jenkins-automation-hub-app -p 8082:8000 jenkins-automation-hub:latest'
            }
        }

    }
}
