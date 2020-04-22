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
                sh "docker build ."
            }
        }
    }
}