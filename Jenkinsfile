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
            steps {
                sh '(aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 482283577367.dkr.ecr.us-east-2.amazonaws.com/jmc/audibene-devops-challenge)'
                sh 'docker build -t jmc/audibene-devops-challenge .'
                sh 'docker tag jmc/audibene-devops-challenge:latest 482283577367.dkr.ecr.us-east-2.amazonaws.com/jmc/audibene-devops-challenge:latest'
                sh 'docker push 482283577367.dkr.ecr.us-east-2.amazonaws.com/jmc/audibene-devops-challenge:latest'
            }
        }
    }
}