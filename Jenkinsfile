pipeline {
  agent any
  options { timestamps() }
  environment {
    COMPOSE_PROJECT_NAME = 'biblioteca_ci'
    API_PORT = '18000'
    MYSQL_PORT = '13306'
  }
  stages {
    stage('Verificar herramientas') {
      steps {
        sh 'docker --version'
        sh 'docker compose version'
      }
    }
    stage('Build') {
      steps { sh 'docker compose build' }
    }
    stage('Levantar servicios') {
      steps { sh 'docker compose up -d' }
    }
    stage('Prueba') {
      steps {
        sh '''
          for i in $(seq 1 40); do
            if docker compose exec -T api python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/prueba-db').status==200 else 1)"; then
              echo "API y MySQL funcionando"
              exit 0
            fi
            echo "Esperando servicios... intento $i"
            sleep 3
          done
          docker compose logs
          exit 1
        '''
      }
    }
  }
  post {
    always { sh 'docker compose down -v || true' }
  }
}
