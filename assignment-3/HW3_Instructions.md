# Homework 3: Deployment Gone Wrong

## Introduction

Right when you thought things couldn't get worse, your company decided to
re-hire Shoddycorp's Cut-Rate Contracting again. They say that you've
done a fantastic job cleaning up their code, and that they're sure you
can handle whatever problems may occur in the next project. It seems they will
never learn.

Now that the web application is fixed and ready, your company wants it
deployed in a scalable, reliable, and secure manner. To do this, your
company hired Shoddycorp's Cut-Rate Contracting to containerize your
application, then deploy it in a way that ensures availability and security.
What they delivered, as usual, falls quite short of the mark.

Like last time, what Shoddycorp's Cut-Rate Contracting provided was a deployment
that *almost* works. They containerized the application, the database, and an
Nginx reverse proxy all in Docker. They then created Kubernetes yaml files to
run these containers in a Kubernetes cluster, and configured them to talk to
each other as needed. They even began adding some event monitoring for a
monitoring software called Prometheus, though they didn't finish it.

However, upon further inspection we can see that they didn't quite do things
right. They left secrets lying around out in the open, they only create one
replica of each pod, and there are passwords getting logged all over the
place. All-in-all, it's a mess.

It looks like the job to fix this falls to you, again. Luckily Kevin Gallagher
(KG) has read through the files already and pointed out some of the things that
are going wrong, and provided a list of things for you to fix. Before you can
work on that, though, let's get your environment set up.

Just a disclaimer, in case it needs to be said again: 
Like with all Shoddycorp's Cut-Rate Contracting deliverables, this is not code
you would like to mimic in any way.

## Frequently Asked Questions

Kubernetes is a fairly complicated beast. To help you get oriented, we've created a [Frequently Asked Questions](FAQ.md) document that should help with common questions. As, always, please make use of office hours and ask questions by email or Slack when you run into trouble!

## Part 0: Setting up Your Environment

In order to complete this assignment you will need Docker, minikube, and 
kubectl. Installing these is not simple, and is highly platform dependent.
Rather than detail how to install these software on different platforms, this
document instead links to the relevant information on how to install these tools
at their official sites.

To install Docker, please see the following Website and select Docker Desktop.

https://www.docker.com/get-started

To install Kubectl, please see the following Website.

https://v1-18.docs.kubernetes.io/docs/tasks/tools/install-kubectl/

To install Minikube, please see the following Website.

https://v1-18.docs.kubernetes.io/docs/tasks/tools/install-minikube/

Like in the previous assignments we will be using Git and Github for submission,
so please ensure you still have Git installed. Though we will not be checking
for them, remember that it is in your best interest to continue to follow git
best practices.

When you are ready to begin the project, please use GitHub Classroom to create
your repository for this assignment, and do your work in that repository. The
repository name will look like `NYUAppSec/assignment-3-[username]`.

### Part 0.1: Rundown of Files

This repository has a lot of files. The following are files you will likely be
modifying throughout this assignment.

* GiftcardSite/GiftcardSite/settings.py
* GiftcardSite/LegacySite/views.py
* GiftcardSite/k8/django-deploy.yaml
* db/Dockerfile
* db/k8/db-deployment.yaml

In addition, you may need to make new files to work with Prometheus, as
described in Part 2.

### Part 0.2: Getting it to Work 

Once you have installed the necessary software, you are ready to run the whole thing
using minikube. First, start minikube.

```
minikube start
```

You will also need to set things up so that docker will use minikube, by running:

```
eval $(minikube docker-env)
```

Next,  we need to build the Dockerfiles Kubernetes will use to create the
cluster. This can be done using the following lines, assuming you are in the
root directory of the repository.

```
docker build -t nyuappsec/assign3:v0 .
docker build -t nyuappsec/assign3-proxy:v0 proxy/
docker build -t nyuappsec/assign3-db:v0 db/
```

Then use kubectl to create the pods and services needed for our project. Again,
these commands assume you are in the root directory of the repository.

```
kubectl apply -f db/k8
kubectl apply -f GiftcardSite/k8
kubectl apply -f proxy/k8
```
Verify that the pods and services were created correctly.

```
kubectl get pods
kubectl get service
```

There should be three pod entries:

* One that starts with assignment3-django-deploy
* One that starts with mysql-container
* One that starts with proxy

They should each have status RUNNING after approximately a minute.

There should also be four service entries:

* One called kubernetes
* One called assignment3-django-service
* One called mysql-service
* One called proxy-service

To see if you can connect to the site, run the following command:

```
minikube service proxy-service
```

This should open your browser to the deployed site. You should be able to view
the first page of the site, and navigate around. If this worked, you are ready
to move on to the next part.

## Part 1: Securing Secrets.

Unfortunately there are many values that are supposed to be secret floating
around in the source code and in the yaml files. Typically we do not want this.
Secret values should be protected so that we can move the source code to GitHub
and put the docker images on Dockerhub and not compromise any secrets. In
addition to keeping secrets secret, this method also allows for changing secrets
more easily.

For this part, your job will be to find some the places in which secrets are
used and replace them with a more secure way of doing secrets. Specifically,
you should look into Kubernetes secrets, how they work, and how they can be
used with both kubernetes yaml files and how they may be accessed via Python
(hint: they end up as environment variables). You may want to read the
[Kubernetes documentation on
secrets](https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/).

For this portion of the assignment, you should submit:

1. All kubernetes yaml files modified to use secrets
2. All changes necessary to the Web application (limited to 
   settings.py as mentioned above) needed to use the passed secrets.
3. A file, called secrets.txt, which demonstrates how you added the secrets.
   This must include all commands used, etc.

Finally, rebuild your Docker container for the Django application, and then
update your pods using the kubectl apply commands specified earlier.

## Part 2: Monitoring with Prometheus

It seems the DevOps employee at Shoddycorp's Cut-Rate Contracting decided to add
some monitoring to the Web application using Prometheus. However, while they do
seem to know how to use the Python Prometheus client to perform monitoring, they
seem to struggle with understanding what your company may want to monitor. More,
they seem to be using Prometheus' monitoring to monitor things that you want to
remain secret!

As if that wasn't bad enough, it seems that the employee also didn't complete
the Prometheus setup! While there is some monitoring there, there is no
Prometheus service to collect the information that's being exposed on the site.

In this section of the assignment you will be fixing this situation by removing
problematic monitoring done using Prometheus' python client, and expanding the
reasonable monitoring with a few more metrics. Then you will create a Prometheus
pod and service for Kubernetes so it can monitor your application.

Specifically, in this part you must:

### Part 2.1: Remove unwanted monitoring.

There exists some unsafe monitoring of sensitive data in views.py. Remove all
monitoring that exposes any sensitive secrets.

All changes in this section should occur in the GiftcardSite/LegacySite/views.py
file.

### Part 2.2: Expand reasonable monitoring.

There are things we may want to monitor using Prometheus. In this part of the
assignment you should add a Prometheus counter that counts all of the times we 
purposely return a 404 message in views.py. These lines are caused by Database 
errors, so you should name this counter database_error_return_404.

All changes in this section should occur in the GiftcardSite/LegacySite/views.py
file.

### Part 2.3: Add Prometheus

All of this data is pointless if it is not being collected. In this section you
should add Prometheus to your Kubernetes cluster and use it to automatically
monitor the metrics from your Web application. Information about how to add
Prometheus to Kubernetes can be found at the following links.

https://prometheus.io/docs/introduction/overview/

For this section you will submit all of the yaml files that you needed to run
Prometheus, as well as a writeup called `prometheus.txt` describing the steps you
took to get it running.


Hints:

* You probably want to look into `helm`, a package manager for kubernetes that makes it easy to install services like Prometheus.

* To configure Prometheus you probably want to use `configmaps`, which are a way of providing configuration information to running pods. You can see what configmaps are available by using `kubectl get configmaps`, and output their current configuration by doing `kubectl get configmap <service_name> -o yaml`. You can also directly edit the configuration with `kubectl edit configmap <service_name>`.

* Each running service gets a DNS name that corresponds to the service name. So to refer to the proxy running on port 8080, you would use `proxy-service:8080`.

## Grading

Total points: 100

Part 0 is worth 10 points, but you are not required to submit anything; just get everything up and running!

Part 1 is worth 60 points:

* 30 points for the yaml files that use Kubernetes secrets.
* 15 points for the changes to the Django code.
* 15 points for the writeup.

Part 2 is worth 30 points:

* 5 points for removing dangerous monitoring
* 5 points for expanding monitoring
* 10 points for all yaml files for Prometheus
* 10 points for the writeup.

## What to Submit

The repository should contain:

* Part 1
  * Your yaml files using Kubernetes secrets.
  * All files you changed from the GiftcardSite/ directory.
  * A writeup called secrets.txt.
* Part 2
  * A modified GiftcardSite/LegacySite/views.py file.
  * Your yaml files for running Prometheus.
  * A writeup called Prometheus.txt.

## Concluding Remarks

With the changes you made in this assignment, your company is a lot closer to a
decent deployment solution. However, even with the changes, there are a lot of
things that are still lacking.

One of the benefits of using Kubernetes is the ability to create replicas that
are load balanced to avoid overwhelming one instance of the application. The
same can be done with other micro-services such as the database, though this
would require database syncing across the difference database instances. These
solutions do not currently exist in this version of the assignment.

For more experience working with cloud security and deployment, consider taking
this one step further and replicating these micro-services. Attempt to load
balance over many replicas, and syncing databases. Try using Prometheus to
gather more metrics from all of your different micro-services. Try adding logging
and other useful tools.

Though these attempts will not be graded, and should not be submitted as part of
the assignment, they should help you learn a lot about how using cloud
deployment helps you preserve the availability of your service (and the
micro-services that comprise it) and how good monitoring and logging can help you
spot errors in the application before they become serious issues.
