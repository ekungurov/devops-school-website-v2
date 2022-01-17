pipeline {
  agent any

  environment {
    AWS_REGION = 'eu-central-1'
  }

  stages {
    stage('SonarQube analysis') {
      agent {
        docker { image 'sonarsource/sonar-scanner-cli:latest' }
      }

      steps {
        checkout scm
        withSonarQubeEnv('SonarCloud') {
          sh 'sonar-scanner'
        }
      }
    }

    stage('Build image') {
      steps {
        checkout scm
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
      agent {
        docker { image 'bitnami/kubectl' }
      }

      steps {
        checkout scm
        withCredentials([usernamePassword(credentialsId: 'aws-token', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
          withKubeConfig([credentialsId: 'kube-config-file']) {
            sh 'kubectl apply -f k8s/'
          }
        }
      }
    }
  }
}
