pipeline {
    agent any
    stages {
        stage('Clone') {
            steps {
               git branch: 'main', url: 'https://github.com/tiennt99/FlaskApiDocs.git'
            }
        }
    }
}