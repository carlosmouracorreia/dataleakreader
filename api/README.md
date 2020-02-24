# Data Leak Reader

Load Data Leak from .txt files into memory-database redis to have fast lookups for email-domain-leak info and even faster writes for bulk email data.

## Software Needed

Docker CLI with Docker-Compose

## Basic Info

1. Create data folder in the root directory and add {data_leak_name}.txt files
2. Run docker-compose up -d on the root folder
3. Navigate to a rest API client/browser with the following address: http://localhost:5051/info?type=<email|domain>&query=<email_add|domain>
4. Add additional limit (less than 50 records) and offset parameters: [...] &limit=50&offset=0 

## Configurable Parameters

In the docker-compose.yml file you can configure the batch size to send to Redis at a time and the regularity to run the workers