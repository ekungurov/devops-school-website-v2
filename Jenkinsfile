pipeline {
  agent any

  environment {
    AWS_REGION = 'eu-central-1'
  }

  stages {
    stage('Clone repository') {
      steps {
        checkout scm
      }
    }

    stage('SonarQube analysis') {
      steps {
        withSonarQubeEnv('SonarCloud') {
          sh 'sonar-scanner'
        }
      }
    }

    stage('Build image') {
      steps {
        script {
          app = docker.build("ekungurov/myapp")
          docker.withRegistry('https://registry.hub.docker.com', 'docker_creds') {
            app.push("0.0." + "${env.BUILD_NUMBER}")
            app.push("latest")
          }
        }
      }
    }

    stage('Deploy to eks') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'aws-token', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
          withKubeConfig([credentialsId: 'kube-config-file']) {
            sh 'kubectl apply -f k8s/'
          }
        }
      }
    }
  }
}
