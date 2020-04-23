```master```: [![Build Status](https://jenkins.jmorgancusick.com/buildStatus/icon?job=John+Cusick%2Faudibene-devops-challenge%2Fmaster)](https://jenkins.jmorgancusick.com/job/John%20Cusick/job/audibene-devops-challenge/job/master/)

```develop```: [![Build Status](https://jenkins.jmorgancusick.com/buildStatus/icon?job=John+Cusick%2Faudibene-devops-challenge%2Fdevelop)](https://jenkins.jmorgancusick.com/job/John%20Cusick/job/audibene-devops-challenge/job/develop/)

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


# Feature Implementation

* **Pull Request Commits**

    * Trigger tests: Pull requests kick off a Jenkins build due to the ```https://jenkins.jmorgancusick.com/github-webhook/``` supplying all events to the Jeknins server. Tests are run in the first stage of the Jenkinsfile's pipeline.
    
* **Commits/Merges into ```develop```**

    * Run tests: I used the same implementation to kick off Jenkins builds on commits/merges into ```develop``` as I did for pull request commits. Tests are run in the same stage.
    
    * Docker build: This and all following steps are only executed in the ```develop``` branch. I accomplished this with Jeknins's ```when``` directive and built-in ```branch``` condition. The build is a simple call to docker build, in part because I designed the Dockerfile to default all arguments to production values.
    
    * Push built image to ECR: Several steps are required in order to authenticate, tag and ultimately push the docker image to Amazon Elastic Container Registry (ECR). The ```jenkins``` user on the Jenkins server has access to the Amazon Web Service (AWS) Command Line Interface (CLI). The AWS CLI is configured with a corresponding ```jenkins``` user on AWS Identity and Access Management (IAM), who has full access to Amazon Elastic Container Registry (ECR). The AWS CLI is used to help login to docker with the proper credentials and gain access to Amazon ECR from the Jenkins server. Once access is gained and the docker build is complete, it's only a matter of tagging the image and pushing it to up to Amazon ECR.
    
    * Deploy code to Kubernetes: I used Amazon Elastic Kubernetes Service (EKS) to create a Kubernetes cluster. The aforementioned AWS IAM ```jenkins``` user must have EKS permissions *and* be granted ```system:masters``` permissions in the cluster's RBAC configuration (guide [here](https://docs.aws.amazon.com/eks/latest/userguide/add-user-role.html)). With these permissions in place, the Jenkins server's ```jenkins``` user can access EKS with a properly configured ```kubectl```. I then built a deployment (```templates/deployment.yaml```) file for my django-admin web server, which consisted of one deployment with one pod and one load balancing service. The most interesting part of the deployment file is the image definition, which uses a variable instead of a hardcoded name and tag. This variable will be used to substitute images in by Helm, which was introduced when the need for rollbacks arose (see "Rollback in case of failure" below). Helm is a package manager for Kubernetes, but for this project I mostly leverage its templated Kubernetes resources ("charts") and rollback utilities. Helm is used in place of ```kubectl``` to deploy the Kubernetes application. Instead of tags, I use digests to identify containers, for better auditing and security. The digest of the image built in the previous step is substituted for the ```deployment.yaml```'s image variable. Helm then upgrades the Kubernetes cluster to the new build.
    
    * Rollback in case of failure: Similar to ```kubectl apply```, Helm does not verify a deployment after resources are created. With helm, one can use ```--wait``` and ```--timeout``` to verify that a deployment was successful before exiting. On top of that, ```--rollback``` can be used along with a revision number to rollback a deployment. Helm saves you from parsing the revision number by wraping all these features into one argument: ```--atomic```. Enabling the atomic option for a ```helm upgrade``` command will also enable ```--wait```, and automatically rollback if a deployment fails! This can be verified by intentionally breaking the build (example [here](https://jenkins.jmorgancusick.com/job/John%20Cusick/job/audibene-devops-challenge/job/develop/27/console)).

* **Commits/Merges into ```master```**

    * Promotes code to master branch: This functionality is provided by Git. Deployment will not be run because of the aforementioned ```when``` directive and ```branch``` condition.
