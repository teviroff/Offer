# Offer

## Run locally

This section explains on how to run project on your local machine.

### Create `dbconfig.py` file

To do so run `setup/dbconfig.bat` script, or, if not supported by your shell, copy contents of
`setup/example_dbconfig.py` to `dbconfig.py`, **located in project root directory.** Then you should fill 
the required fields with your database connection details.

> For PostgreSQL connection data should be taken directly from `docker-compose.yml`.
> Other databases require more precise configuration add will be discussed later.

### Docker setup

All services used by project are deployed via Docker containers. First step to launch them is to 
install Docker Desktop as well as Docker CLI (they are usually bundled together). Then you 
might want to change some settings in `docker-compose.yml`. If you want to run entire application 
with Docker (when deploying, for example), look at [deployment guide](#deployment-guide) section.
There we will focus on running only database containers. To do so comment out `app` service and 
all network configurations from `docker-compose.yml` and run `docker-compose up --build`. After 
launching containers, ports, needed for `dbconfig.py`, can be viewed in Docker Desktop.

### MongoDB configuration

To start configuration make sure that you are running `mongodb_container` in Docker and have 
MongoDB Compass installed. Open Compass and create new database connection depending on your 
`docker-compose.yml` file. Usually, you would connect to `mongodb://localhost:27017`. Note that 
you should provide authentication info in connection string. To do so navigate to 
`Edit connection > Advanced Connection Options > Authentication` and write there credentials for 
admin user of your database. Normally they should be identical to those specified in 
`docker-compose.yml`. 

If you started a fresh instance of a MongoDB container, you will be met with cluster of three 
databases: `admin`, `config` and `local`. To proceed create new database, with two collections: 
`opportunity_form` and `response_data`. Newly created database name should be put in `dbconfig.py`.

Next step is to create user, that will operate on this database. To do so open database shell 
by clicking chell icon, that appears when active connection is hovered. After opening shell 
following commands can be used to create user:

```
use offer
db.createUser({
    user: "mongo",
    pwd: "admin",
    roles: [{ role: "readWrite", db: "offer" }]
})
```

And like that you created user, whose credentials should be put in `dbconfig.py`.

### MinIO configuration

To start configuration make sure that you are running `minio_container` in Docker. First thing 
to do is to open MinIO WebUI service. To do so open `minio_container` logs. There you will find 
a lot of system messages as well as message looking like this: 

> 2024-12-03 14:50:57 WebUI: http://172.19.0.3:9001 http://127.0.0.1:9001

To open UI click any of the links from such message. After doing so you will arrive at authorization 
page of MinIO. Credentials to enter here are `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` 
from `docker-compose.yml`. After all this you should arrive at database administration page. 
There you have several things to do. 

Firstly, you should obtain access keys for `dbconfig.py`. To do so navigate to `Access Keys` page 
and click `Create access key` button. After all the required steps you should be able to obtain 
both access key and private key. They must be put in `dbconfig.py`.

Secondly, you should initialize some buckets that are used by application. To do so navigate to 
`Buckets` page and click `Create Bucket` button. Buckets you need to create are: `user-avatar`, 
`user-cv`, `opportunity-provider-logo` and `opportunity-description`. 

Lastly, some of the created buckets must have default files. Following list describe all of them:
* `user-avatar` must have `default.png` file.
* `opportunity-provider-logo` must have `default.png` file, as well.
* `opportunity-description` must have `default.md` file.

> Default files are currently used only by website, so they are not required if you are only willing 
> to use API, however this might change in the future.

## Deployment guide

...
