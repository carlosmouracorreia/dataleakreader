# Data Leak Reader - Dumper + API

Loads email bulk data from .txt files into memory-database redis to have fast lookups for email-domain-leak info (with a **Flask API**) and even faster writes for bulk email data with a **Celery Beat** powered worker.

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

## Example Outputs

Test


## Configurable Parameters
 In the .env file you can configure some application specific parameters before you rebuild the app with docker-compose up -d --build

 * **BATCH_SIZE_WRITE** - the batch size to send to Redis at a time
 * **WORKER_TRIGGER_SECOND_FREQUENCY** - the regularity to run the workers
 * **MAX_LIMIT_OUTPUT** - the max limit to be outputed on the results list

 ## Speed Considerations

Test