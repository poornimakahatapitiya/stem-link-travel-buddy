pipeline {
  agent any

  options {
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timestamps()
  }

  parameters {
    string(name: 'BRANCH', defaultValue: 'main', description: 'Git branch to build')
    string(name: 'AWS_REGION', defaultValue: 'us-east-1', description: 'AWS region')
    string(name: 'SSM_PARAM_NAME', defaultValue: '/my-app/config', description: 'SSM parameter name containing config.json')
    string(name: 'ECR_REPO', defaultValue: 'my-app', description: 'ECR repository name (without env suffix)')
    string(name: 'ECS_CLUSTER', defaultValue: 'my-cluster', description: 'ECS cluster name')
    string(name: 'ECS_SERVICE', defaultValue: 'my-service', description: 'ECS service name')
    string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Image tag to push (e.g., latest)')
  }

  environment {
    REGION = "${params.AWS_REGION}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout([
          $class: 'GitSCM',
          branches: [[name: "*/${params.BRANCH}"]],
          userRemoteConfigs: [[
            url: 'https://github.com/<ORG>/<REPO>.git'
            // If private repo: add credentialsId: 'github-creds'
          ]]
        ])
      }
    }

    stage('Verify AWS Identity') {
      steps {
        sh "aws sts get-caller-identity"
      }
    }

    stage('Fetch config.json from SSM') {
      steps {
        sh """
          mkdir -p ./src/main
          aws ssm get-parameter \
            --name "${params.SSM_PARAM_NAME}" \
            --with-decryption \
            --query "Parameter.Value" \
            --output text > ./src/main/config.json
        """
      }
    }

    stage('ECR Login') {
      steps {
        script {
          env.AWS_ACCOUNT_ID = sh(
            script: "aws sts get-caller-identity --query Account --output text",
            returnStdout: true
          ).trim()
          env.ECR_REGISTRY = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${env.REGION}.amazonaws.com"
          env.ECR_URI = "${env.ECR_REGISTRY}/${params.ECR_REPO}"
        }

        sh """
          aws ecr get-login-password --region ${env.REGION} \
            | docker login --username AWS --password-stdin ${env.ECR_REGISTRY}
        """
      }
    }

    stage('Build & Push Image') {
      steps {
        sh """
          set -e
          docker build -t ${params.ECR_REPO}:${params.IMAGE_TAG} .
          docker tag ${params.ECR_REPO}:${params.IMAGE_TAG} ${env.ECR_URI}:${params.IMAGE_TAG}
          docker push ${env.ECR_URI}:${params.IMAGE_TAG}
        """
      }
    }

    stage('Deploy (Force New Deployment)') {
      steps {
        sh """
          set -e
          aws ecs update-service \
            --region ${env.REGION} \
            --cluster "${params.ECS_CLUSTER}" \
            --service "${params.ECS_SERVICE}" \
            --force-new-deployment

          aws ecs wait services-stable \
            --region ${env.REGION} \
            --cluster "${params.ECS_CLUSTER}" \
            --services "${params.ECS_SERVICE}"

          echo "ECS service is stable after force new deployment."
        """
      }
    }
  }

  post {
    always {
      sh 'docker rmi ${ECR_URI}:${IMAGE_TAG} || true'
      sh 'docker rmi ${ECR_REPO}:${IMAGE_TAG} || true'
      sh 'docker rmi $(docker images -f "dangling=true" -q) || true'
      cleanWs()
    }
  }
}
