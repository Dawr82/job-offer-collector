# job-offer-collector
This application aims at collecting job-related data from various polish job listing websites.  
Due to its microservice architecture, it can be easily deployed as Docker containers (docker-compose preferably)  
or in other container-based environments (like Kubernetes).

The application consists of following components:
* Scraper (core of the application) - gathering job-related data from the internet
* REST API - exposing gathered data to the external world
* Frontend - visualizing gathered data through a handful of charts
* MongoDB - persisting gathered data
* Redis - caching data for REST API server  

There are also Kubernetes .yaml manifest files meant for the deployment of this application in Kubernetes cluster.

Scraper part of the application provides user interface (CLI) that allows
for chosing the mode that the scraper operates in.
