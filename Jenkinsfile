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
                    additionalBuildArgs '--build-arg DJANGO_UID=$(id -u $USER) --build-arg DJANGO_GID=$(id -g $USER) --build-arg PIPENV_ARGS="--dev"'
                }
            }
            steps {
                // use single quote so that $HOME isn't exanded by groovy
                sh '(cd $HOME && pipenv run python3 -m pytest .)'
            }
        }
    }
}