node {
  def app
  
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
}
