# audibene-devops-challenge
A default django-admin server

Build with:

~~~
docker build . -t django-admin
~~~


Run with:

~~~
docker run -p 8000:8000 django-admin
~~~

Then connect to 127.0.0.1:8000


# Feature Explanation

* **Pull Request Commits**

    * Trigger tests: Pull requests kick off a Jenkins build due to the ```https://jenkins.jmorgancusick.com/github-webhook/``` supplying all events to the Jeknins server. Tests are run in the first stage of the Jenkinsfile's pipeline.
    
* **Commits/Merges into ```develop```**

    * Run tests: I used the same implementation to kick off Jenkins builds on commits/merges into ```develop``` as I did for pull request commits. Tests are run in the same stage.
    
    * Docker build: This and all following steps are only executed in the ```develop``` branch. I accomplished this with Jeknins's ```when``` directive and built-in ```branch``` condition. The build is a simple call to docker build, in part because I designed the Dockerfile to default all arguments to production values.
    
    * Push built image to ECR: Several steps are required in order to authenticate, tag and ultimately push the docker image to Amazon Elastic Container Registry (ECR). The ```jenkins``` user on the Jenkins server has access to the Amazon Web Service (AWS) Command Line Interface (CLI). The AWS CLI is configured with a corresponding ```jenkins``` user on AWS Identity and Access Management (IAM), who has full access to Amazon Elastic Container Registry (ECR). The AWS CLI is used to help login to docker with the proper credentials and gain access to Amazon ECR from the Jenkins server. Once access is gained and the docker build is complete, it's only a matter of tagging the image and pushing it to up to Amazon ECR.
    
    * Deploy code to Kubernetes:  
    
    * Rollback in case of failure:

* **Commits/Merges into ```master```**

    * Promotes code to master branch:
