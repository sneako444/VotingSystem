pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/sneako444/VotingSystem.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build('online-voting-app')
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh 'python manage.py test'
            }
        }
    }
}
