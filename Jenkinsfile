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
      agent {
        docker { image 'sonarsource/sonar-scanner-cli:latest' }
      }

      steps {
        withSonarQubeEnv('SonarCloud') {
          sh 'sonar-scanner'
        }
      }
    }

    stage('Build image') {
      agent {
        docker { image 'docker:dind' }
      }

      steps {
        script {
          app = docker.build("ekungurov/myapp")
          docker.withRegistry('https://registry.hub.docker.com', 'docker_creds') {
            if (env.IMAGE_TAG != "latest") {
              app.push("${env.IMAGE_TAG}")
            }
            app.push("latest")
          }
        }
      }
    }

    stage('Deploy to eks') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'aws-token', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
          withKubeConfig([credentialsId: 'kube-config-file']) {
            sh "sed -i 's/__TAG__/${env.IMAGE_TAG}/g' k8s/deployment.yml"
            sh 'kubectl apply -f k8s/'
          }
        }
      }
    }
  }
}
