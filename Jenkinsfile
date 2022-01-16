node {
  def app

  environment {
    AWS_REGION = 'eu-central-1'
  }
  
  stage('Clone repository') {
    checkout scm
  }

  stage('SonarQube analysis') {
    withSonarQubeEnv('SonarCloud') {
      sh 'sonar-scanner'
    }
  }
  
  stage('Build image') {
    app = docker.build("ekungurov/myapp")
  }
  
  stage('Push image') {
    docker.withRegistry('https://registry.hub.docker.com', 'docker_creds') {
      app.push("0.0." + "${env.BUILD_NUMBER}")
      app.push("latest")
    }
  }

  stage('Deploy to eks') {
    withCredentials([usernamePassword(credentialsId: 'aws-token', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
      withKubeConfig([credentialsId: 'kube-config-file']) {
        sh 'kubectl apply -f k8s/'
      }
    }
  }
}
