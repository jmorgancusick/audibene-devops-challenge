pipeline {
    agent any
    triggers {
        cron("@daily")
    }
    stages {
        stage("test") {
            agent {
                dockerfile {
                    args "-u django:django"
                    // use single quote to defer interpolation
                    additionalBuildArgs '--build-arg DJANGO_UID=$(id -u $USER) --build-arg DJANGO_GID=$(id -g $USER) --build-arg PIPENV_DEV="true"'
                }
            }
            steps {
                // use single quote to defer interpolation
                sh '(cd $HOME && pipenv run python3 -m pytest .)'
            }
        }
        stage("develop-branch-deploy") {
            when {
                branch "develop"
            }
            environment {
                // set PATH to use most recent aws cli
                PATH = "/usr/local/bin:$PATH"
            }
            steps {
                // AWS IAM authentication configured in ~/.docker/config.json, login not required

                // Build and tag
                sh 'docker build -t jmc/audibene-devops-challenge .'
                sh 'docker tag jmc/audibene-devops-challenge:latest 482283577367.dkr.ecr.us-east-2.amazonaws.com/jmc/audibene-devops-challenge:latest'

                // Push to AWS ECR
                sh 'docker push 482283577367.dkr.ecr.us-east-2.amazonaws.com/jmc/audibene-devops-challenge:latest'

                // Deploy to AWS EKS, rollback on failure
                sh 'helm upgrade --install --atomic --timeout 30s --set image.id=$(docker inspect --format="{{index .RepoDigests 0}}" 482283577367.dkr.ecr.us-east-2.amazonaws.com/jmc/audibene-devops-challenge:latest) django-admin .'
            }
        }
    }
    post {
        cleanup {
            cleanWs()
        }
    }
}
