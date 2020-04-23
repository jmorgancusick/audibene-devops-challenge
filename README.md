```master```: [![Build Status](https://jenkins.jmorgancusick.com/buildStatus/icon?job=John+Cusick%2Faudibene-devops-challenge%2Fmaster)](https://jenkins.jmorgancusick.com/job/John%20Cusick/job/audibene-devops-challenge/job/master/)

```develop```: [![Build Status](https://jenkins.jmorgancusick.com/buildStatus/icon?job=John+Cusick%2Faudibene-devops-challenge%2Fdevelop)](https://jenkins.jmorgancusick.com/job/John%20Cusick/job/audibene-devops-challenge/job/develop/)

# audibene-devops-challenge

This is a default Django admin web server running on Amazon EKS. It is live at http://a635be4af311c43b4b3761316d793b22-1623537517.us-east-2.elb.amazonaws.com/

Deployments are handled by a Jenkins server. With username ```guest``` and password ```guest```, the associated Jenkins repository can be viewed at https://jenkins.jmorgancusick.com/job/John%20Cusick/job/audibene-devops-challenge/

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


# Assumptions



# Further Comments

* By default ```helm```, like ```kubectl```, uses a rolling deployment strategy. Blue/Green or canary deployment strategies could be configured

* The Jenkinsfile and Dockerfile work in tandem to specify the ```django``` user id (uid) and group id (gid) inside the docker agent during the ```test``` stage. This is done to avoid:

   1. Running as a root user inside the container. 
   2. Introducing a configuration dependency between the Jenkinsfile and Jenkins server.
   
   When Jenkins uses a docker container as an agent, it mounts the current workspace to the container as a volume. This mounted volume is owned by the Jenkins server's ```jenkins``` user, or more precisely the ```jenkins``` user's user id and group id. In addition to mounting the volume, Jenkins sets the working directory for the container to the volume. Neither the volume nor the working directory can be overriden by the Jenkinsfile. All of this wouldn't be a problem, except for the fact that ```sh``` steps hang prior to execution if Jenkins does not have write access to the current directory. This is due to attempts to create cache files and files for redirecting stdout/stderr.
   
   Two predominant solutions exist: utilize root user in the container or manually configure your container's user to have the same uid and gid as your Jenkins user. These solutions are equally heinous. Running as a root user in a container introduces a big security vulnerability, while tying your container and Jenkins server's uids/gids together prevents the same pipeline from working on other servers. The latter could even cause conflicts between two repositories on the same server, if they both had a uid/gid requirement. An elegant solution turns out to be the latter, but with a touch of automation. By having Jenkins pass its uid and gid to the container at build time, the crisis can be averted.
   
   
