# Data Leak Reader - Dumper + API

Loads email bulk data from .txt files into memory-database **Redis** to have fast lookups for email-domain-leak info (with a **Flask API**) and even faster writes for bulk email data with a **Celery Beat** powered worker.

By having a folder with text files this software will incrementally save the records in the DB. Also, as new files come in or the existing text files get bigger (imagining they're being constantly fed from a stream to the disk) this app will further increment the respective leak data.

## Software Needed

Docker CLI with Docker-Compose

## Basic Info

1. Create data folder in the root directory and add {data_leak_name}.txt files with an email (utf8-encoded) per line
2. Run docker-compose up -d on the root folder
3. Navigate to a rest API client/browser with the following address: http://localhost:5051/info

## API Parameters
The API exposes only one endpoint:
{base_url}/info

The **required query parameters** are:

* type: **emails_leaks_from_domain** to lookup by domain and **leaks_from_email** to lookup by email
* query: either an email or a domain

limit and offset are **optional** and allow to skip/limit records

## Example API Outputs

* **emails_leaks_from_domain** - Lookup by domain

```
{
  "emails_leaks_from_domain": [
    {
      "email": "blues@orangemail.sk",
      "leak": "neopets"
    }, 
   ],
  "pagination": {
    "element_nr": 31,
    "limit": 150,
    "offset": 0
  },
  "total_email_nr": "11364001"
}

```

* **leaks_from_email** - Lookup by email


```
{
  "leaks_from_email": [
    "linkedinsample",
    "neopets"
  ],
  "pagination": {
    "element_nr": 2,
    "limit": 150,
    "offset": 0
  },
  "total_email_nr": "11056801"
}

```

## Configurable Parameters
 In the **.env** root level file you can configure some application specific parameters before you rebuild the app with docker-compose up -d --build

 * **BATCH_SIZE_WRITE** - the batch size to send to Redis at a time
 * **WORKER_TRIGGER_SECOND_FREQUENCY** - the periodicity to run the workers against
 * **MAX_LIMIT_OUTPUT** - the max limit to be outputed on the results list


## Data Structure

A simple key value data structure was used following Redis unstructured nature.
Redis was used instead of a disk persistent storage in order to speed up lookups and writes (even faster than reads). A combo with an incremental indexed database for cleaned records (after parsing etc) could be a next iteration on this project.

The keys used for this implementation are:

* **DOMAIN-{domain-name}** - Contains a list of JSON strings (then de-serialized) with the following attributes: email and data_leak
* **EMAIL-{email-address}** - Contains a list of strings with the respective data-leak
* **META-FILE-CHANGED_{leak_name}** - The periodic worker only takes action on the i-th coming file from the data folder after the 1st dump if the file has been changed again
* **META-FILE-LINES-NR_{leak_name}** - Goes in hand with the previous metadata - fast fowards to the last stored line from the last changed date and only starts dumping from there
* **META-FILE-TASK-RUNNING_{leak_name}** - The worker was built in a naive way, spawning as many workers as the number of existing files per seconds fraction. This flag is a trick to not allow multiple workers to be working on the same file at the same time (usually files are big and take more time to process than the frequency-interval cronjobs) to avoid data duplication.  

**DUPLICATION** was not strictly checked against yet as there might be some race conditions prone to happen this way. Also, the provided files can have duplicated entries and naively checking for existing entries would slow down the lookup/writes so no solution was implemented yet.

## Speed Considerations 

Most of these are empirically thought through and not formally clock tested. Also, most of them are arguably order of relevance. The obvious one is that we're not persisting data to disk.

1. Using the aforementioned data structure while resulting in data duplicating it will speed up lookups
2. Using a Redis Pipeline will cut Round Trip Times by doing less TCP calls to Redis Server
3. Using an acceptable batch size (implemented by this app) for the pipeline means that the API can be looked up while data is being added (and not just on the end)
4. Ignoring non-utf8 characters seems to speed up lookup queries a lot when dumper is importing data
5. Using limits for querying data speeds up the information retrieval
6. Using a different Redis server (as a docker instance) for Celery Workers/Beat and another one for our data structure might cut down on server resource exaustion and thus speeding things.
7. Gunicorn server spawned with 4 workers

## Security Considerations

This program was done as a trial for an information security company so at least a brief statement about securing data should be written even if it wasn't the main topic addressed for the task.

1. Only endpoint was secured by sanitizing query types and integers on the input parameters (query parameters)
2. Docker Network concept was used to provide different addresses for the different containers/machines running
3. Database ports were exposed just between the (needed?) containers and the only port exposed to the outside (host-OS) was the server API one.
4. Because all the communication was done within Docker VMs Redis password authentication was not used at this point
5. Gunicorn server opposed/on-top of normal flask server instance will ensure HTTP requests are coherent for a normal-sized app out of the box (e.g by limiting Header Fields/payload)