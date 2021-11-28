# A scalable Web Scraper stack on AWS ECS
> insert Gifs (nhìn gif xong hiểu luôn flow đi thế nào)

"A scalable WebScraper-stack with task-orchestration and data-visualization"

Architecture: WebScraper-stack (Selenium, Airflow, PostgreSQL, Metabase) deployed on AWS ECS with a Load Balancer.
> insert image Architecture


## Objectives & Design
- Objectives: create a overview of real estate market in Saigon through a dashboard from crawled data.
- Design: Airflow on ECS to orchestrate Crawling/Cleaning/Loading, PostgreSQL for storing cleaned data, Metabase for visualization.
- [Metabase dashboard](http://vizlb-1924166062.ap-southeast-1.elb.amazonaws.com/public/dashboard/88e7d2ac-587d-4343-b7aa-b7a13e881839)

### Deploy Instruction
#### Deploy on Local:
- Presequisite: [Docker Desktop](https://docs.docker.com/engine/install/) with at least 6GB of RAM, [psql](https://formulae.brew.sh/formula/postgresql@13)
- Infra
- docker-compose up

#### Deploy on your AWS: 
- Presequisite: [AWS account](https://aws.amazon.com/), AWS-CLI installed, S3, ECS, EFS, DataSync.
- Infra
- Config
- AWS Infrastructure Cost: $2/day ~ $60/month

### Code Walkthrough
- git clone this repo ```$ git clone https://github.com/ngonam2403/webscraper-data-stack-ecs.git ```
- docker-compose file to deploy on Local
- docker-compose file to deploy on AWS ECS
```yaml

# airflow-stack-docker-compose.yml
# Adapted from: https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml
version: '3'

services:
  redis:
    image: redis:latest
    ports:
      - 6379:6379
    logging:
      driver: awslogs
      options: 
        awslogs-group: ec2-airflow-stack
        awslogs-region: ap-southeast-1
        awslogs-stream-prefix: redis
        
  postgres:
    image: postgres:13.4-alpine 
    environment:
      POSTGRES_HOST_AUTH_METHOD: trust
    ports:
      - 5432:5432
    volumes:
      - /home/ec2-user/efs/webscraper-data-stack-ecs/postgres/airflow-volume/entrypoint/:/docker-entrypoint-initdb.d/:ro
      - /home/ec2-user/efs/webscraper-data-stack-ecs/out/airflow:/out
      - /home/ec2-user/efs/webscraper-data-stack-ecs/postgres/airflow-volume/db:/var/lib/postgresql/data    # persist data & not conflict
    logging:
      driver: awslogs
      options: 
        awslogs-group: ec2-airflow-stack
        awslogs-region: ap-southeast-1
        awslogs-stream-prefix: postgres
    links:
      - redis:redis

  selenium:
    image: selenium/standalone-chrome 
    ports:
        - 4444:4444
    restart: always  
    logging:
      driver: awslogs
      options: 
        awslogs-group: ec2-airflow-stack
        awslogs-region: ap-southeast-1
        awslogs-stream-prefix: selenium


  airflow-init:
    image: ngonam24/airflow-stack
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      # AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__FERNET_KEY: ''
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      AIRFLOW__API__AUTH_BACKEND: 'airflow.api.auth.backend.basic_auth'
      _PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:-}

      _AIRFLOW_DB_UPGRADE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-airflow}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-airflow}

    entrypoint: /bin/bash
    # yamllint disable rule:line-length
    command:
      - -c
      - |
        function ver() {
          printf "%04d%04d%04d%04d" $${1//./ }
        }
        airflow_version=$$(gosu airflow airflow version)
        airflow_version_comparable=$$(ver $${airflow_version})
        min_airflow_version=2.2.0
        min_airflow_version_comparable=$$(ver $${min_airflow_version})
        if (( airflow_version_comparable < min_airflow_version_comparable )); then
          echo
          echo -e "\033[1;31mERROR!!!: Too old Airflow version $${airflow_version}!\e[0m"
          echo "The minimum Airflow version supported: $${min_airflow_version}. Only use this or higher!"
          echo
          exit 1
        fi
        if [[ -z "${AIRFLOW_UID}" ]]; then
          echo
          echo -e "\033[1;33mWARNING!!!: AIRFLOW_UID not set!\e[0m"
          echo "If you are on Linux, you SHOULD follow the instructions below to set "
          echo "AIRFLOW_UID environment variable, otherwise files will be owned by root."
          echo "For other operating systems you can get rid of the warning with manually created .env file:"
          echo "    See: https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html#setting-the-right-airflow-user"
          echo
        fi
        one_meg=1048576
        mem_available=$$(($$(getconf _PHYS_PAGES) * $$(getconf PAGE_SIZE) / one_meg))
        cpus_available=$$(grep -cE 'cpu[0-9]+' /proc/stat)
        disk_available=$$(df / | tail -1 | awk '{print $$4}')
        warning_resources="false"
        if (( mem_available < 4000 )) ; then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough memory available for Docker.\e[0m"
          echo "At least 4GB of memory required. You have $$(numfmt --to iec $$((mem_available * one_meg)))"
          echo
          warning_resources="true"
        fi
        if (( cpus_available < 2 )); then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough CPUS available for Docker.\e[0m"
          echo "At least 2 CPUs recommended. You have $${cpus_available}"
          echo
          warning_resources="true"
        fi
        if (( disk_available < one_meg * 10 )); then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough Disk space available for Docker.\e[0m"
          echo "At least 10 GBs recommended. You have $$(numfmt --to iec $$((disk_available * 1024 )))"
          echo
          warning_resources="true"
        fi
        if [[ $${warning_resources} == "true" ]]; then
          echo
          echo -e "\033[1;33mWARNING!!!: You have not enough resources to run Airflow (see above)!\e[0m"
          echo "Please follow the instructions to increase amount of resources available:"
          echo "   https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html#before-you-begin"
          echo
        fi
        mkdir -p /sources/logs /sources/dags /sources/plugins
        chown -R "${AIRFLOW_UID}:0" /sources/{logs,dags,plugins}
        chown -R "${AIRFLOW_UID}:0" /data
        exec /entrypoint airflow version
    # yamllint enable rule:line-length
    user: "0:0"
    volumes:
      - /home/ec2-user/efs/webscraper-data-stack-ecs:/sources
      - /home/ec2-user/efs/webscraper-data-stack-ecs/data:/data
    logging:
      driver: awslogs
      options: 
        awslogs-group: ec2-airflow-stack
        awslogs-region: ap-southeast-1
        awslogs-stream-prefix: airflow-init
    # hostname: airflow-init
    ports:
      - 8081:8081
    links:
      - redis:redis
      - postgres:postgres


  airflow-webserver:
    image: ngonam24/airflow-stack
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__FERNET_KEY: ''
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      AIRFLOW__API__AUTH_BACKEND: 'airflow.api.auth.backend.basic_auth'
      _PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:-}
    volumes:
      - /home/ec2-user/efs/webscraper-data-stack-ecs/out:/opt/airflow/out
      - /home/ec2-user/efs/webscraper-data-stack-ecs/dags:/opt/airflow/dags
      - /home/ec2-user/efs/webscraper-data-stack-ecs/logs:/opt/airflow/logs
      - /home/ec2-user/efs/webscraper-data-stack-ecs/plugins:/opt/airflow/plugins
      - /home/ec2-user/efs/webscraper-data-stack-ecs/data:/data 
    user: "${AIRFLOW_UID:-50000}:0"
    command: webserver
    ports:
      - 8080:8080
    logging:
      driver: awslogs
      options: 
        awslogs-group: ec2-airflow-stack
        awslogs-region: ap-southeast-1
        awslogs-stream-prefix: airflow-webserver
    # hostname: airflow-webserver
    links:
      - redis:redis
      - postgres:postgres
      - airflow-scheduler:airflow-scheduler
      - selenium:selenium

  airflow-scheduler:
    image: ngonam24/airflow-stack
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__FERNET_KEY: ''
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      AIRFLOW__API__AUTH_BACKEND: 'airflow.api.auth.backend.basic_auth'
      _PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:-}
    volumes:
      - /home/ec2-user/efs/webscraper-data-stack-ecs:/sources
      - /home/ec2-user/efs/webscraper-data-stack-ecs/out:/opt/airflow/out
      - /home/ec2-user/efs/webscraper-data-stack-ecs/dags:/opt/airflow/dags
      - /home/ec2-user/efs/webscraper-data-stack-ecs/logs:/opt/airflow/logs
      - /home/ec2-user/efs/webscraper-data-stack-ecs/plugins:/opt/airflow/plugins
      - /home/ec2-user/efs/webscraper-data-stack-ecs/data:/data 
    user: "${AIRFLOW_UID:-50000}:0"
    command: scheduler
    restart: always
    logging:
      driver: awslogs
      options: 
        awslogs-group: ec2-airflow-stack
        awslogs-region: ap-southeast-1
        awslogs-stream-prefix: airflow-scheduler
    hostname: airflow-scheduler
    links:
      - redis:redis
      - postgres:postgres
      - selenium:selenium


# ecs-params.yml
version: 1
task_definition:
  services:
    redis:
      essential: true
      healthcheck:
        test: ["CMD", "redis-cli", "ping"]
        interval: 5s
        timeout: 5s
        retries: 3
        start_period: 30s
      cpu_shares: 64
      mem_limit: 32MB

    postgres:
      essential: true
      healthcheck:
        test: ["CMD", "pg_isready", "-U", "airflow"]
        interval: 5s
        retries: 3
        start_period: 30s
      cpu_shares: 64
      mem_limit: 128MB

    airflow-init:
      essential: false
      # airflow-init cần ít nhất là [512MB ram,] để run được, còn không thì sẽ báo lỗi.
      cpu_shares: 256
      mem_limit: 512MB
      depends_on:
        - container_name: redis
          condition: HEALTHY
        - container_name: postgres
          condition: HEALTHY

    airflow-webserver:
      essential: false
      cpu_shares: 512
      mem_limit: 1250MB
      healthcheck:
        test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
        interval: 30s
        timeout: 10s
        retries: 5
        start_period: 60s
      depends_on:
        - container_name: redis
          condition: HEALTHY
        - container_name: postgres
          condition: HEALTHY
        - container_name: airflow-init
          condition: SUCCESS

    airflow-scheduler: 
    # Nếu không đủ cpu & ram thì scheduler vẫn hoạt động, nhưng không import gì cả ==> webserver sẽ không thấy gì.
      essential: false
      cpu_shares: 512
      mem_limit: 900MB
      healthcheck:
        test: ["CMD-SHELL", 'airflow jobs check --job-type SchedulerJob --hostname "$${HOSTNAME}"']
        interval: 10s
        timeout: 10s
        retries: 5
        start_period: 60s
      depends_on:
        - container_name: redis
          condition: HEALTHY
        - container_name: postgres
          condition: HEALTHY
        - container_name: airflow-init
          condition: SUCCESS

    selenium:
      essential: false    # khi đi cùng với airflow stack thì để là false.
      cpu_shares: 612     # cpu 512, ram 1gb
      mem_limit: 1GB

```

```yaml
# metabase-docker-compose.yml
version: '3'
services:
  metabase:
    image: metabase/metabase:latest
    volumes: 
      - /home/ec2-user/efs/webscraper-data-stack-ecs/metabase/dev/urandom:/dev/random:ro
      - /home/ec2-user/efs/webscraper-data-stack-ecs/metabase/data:/var/lib
    ports:
      - 3000:3000
    environment: 
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: metabase
      MB_DB_PORT: 5432
      MB_DB_USER: metabaseUser
      MB_DB_PASS: metabaseUserPassword
      MB_DB_HOST: postgres
    logging:
      driver: awslogs
      options: 
        awslogs-group: ec2-metabase
        awslogs-region: ap-southeast-1
        awslogs-stream-prefix: metabase
    links:
      - postgres:postgres
    

  postgres:
    image: postgres:13.4-alpine 
    volumes:
      - /home/ec2-user/efs/webscraper-data-stack-ecs/postgres/metabase-volume/entrypoint/:/docker-entrypoint-initdb.d/:ro      # create user for postgres
      - /home/ec2-user/efs/webscraper-data-stack-ecs/postgres/metabase-volume/db:/var/lib/postgresql/data                      # persist data 
    environment:
      POSTGRES_USER: metabaseUser
      POSTGRES_DB: metabase
      POSTGRES_PASSWORD: metabaseUserPassword
    logging:
      driver: awslogs
      options: 
        awslogs-group: ec2-metabase
        awslogs-region: ap-southeast-1
        awslogs-stream-prefix: postgres


# metabase-ecs-params.yml
version: 1
task_definition:
  services:     
    postgres:
      essential: true
      healthcheck:
        test: ["CMD", "pg_isready", "-U", "metabaseUser"]
        interval: 5s
        retries: 3
        start_period: 30s
      cpu_shares: 64
      mem_limit: 128MB  

    metabase:
      essential: false
      cpu_shares: 1800
      mem_limit: 1.6GB
      healthcheck:
        test: ["CMD", "curl", "--fail", "http://localhost:3000/health"]
        interval: 60s
        timeout: 10s
        retries: 3
        start_period: 60s
      depends_on:
        - container_name: postgres
          condition: HEALTHY


```

- crawl & save to data lake
- clean data 
- load data into postgresql
- AWS CLI 

```bash
aws ec2 create-key-pair \
    --key-name my-key-pair \
    --key-type rsa \
    --query "KeyMaterial" \
    --output text > my-key-pair.pem

export AWS_ID=$(aws sts get-caller-identity --query Account --output text | cat)
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
export AWS_REGION=$(aws configure get region)
export KEY_PAIR="<my-keypair-name>.pem"

export ECS_PROFILE_NAME=profile-ec2-airflow
export ECS_CLUSTER_NAME=cluster-ec2-airflow
export ECS_CLUSTER_CONFIG_NAME=ClusterConfig-ec2-airflow
export ECS_PROJECT_NAME=Project-ec2-airflow

export KEY_PAIR_NAME_ON_AWS=my-key-pair

# Create a profile using your access key and secret key
ecs-cli configure profile \
  --access-key $AWS_ACCESS_KEY_ID \
  --secret-key $AWS_SECRET_ACCESS_KEY \
  --profile-name $ECS_PROFILE_NAME

# Create a cluster configuration
ecs-cli configure --cluster $ECS_CLUSTER_NAME \
  --default-launch-type EC2 \
  --config-name $ECS_CLUSTER_CONFIG_NAME \
  --region $AWS_REGION

# Creating a ECS Cluster with a x86 EC2 Container Instances: t3.medium(2vCPU, 4GB RAM)
ecs-cli up \
  --capability-iam \
  --keypair $KEY_PAIR_NAME_ON_AWS \
  --size 1 \
  --instance-type t3.medium \
  --launch-type EC2 \
  --region $AWS_REGION \
  --cluster-config $ECS_CLUSTER_CONFIG_NAME \
  --ecs-profile $ECS_PROFILE_NAME \
  --vpc $VPC_ID \
  --security-group $SECURITY_GROUP_ID \
  --subnets $SUBNET_1_ID, $SUBNET_2_ID \
  --force 

# Create a S3 bucket


# Sync data from Local to S3 bucket
cd try-default-airflow-docker-ecs/
aws s3 sync . s3://bucket-superset/try-default-airflow-docker-ecs/

# Create a EFS Filesystem for Mounting

# Create a DataSync task to initiate mount & later do specific mounts

```

Mount your EFS filesystem:
- [ssh into your EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html)
- [mount your EFS filesystem to EC2](https://docs.aws.amazon.com/efs/latest/ug/wt1-test.html)
```
mkdir -p efs
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport <your-filesystem-id>.efs.<your-aws-region>.amazonaws.com:/ efs
```

Start a ECS Task
``` 
export COMPOSEFILE=airflow2-origin-docker-compose.yml
export ECS_PROJECT_NAME=Project-ec2-airflow
export ECS_PARAMS=ecs-params.yml

ecs-cli compose --project-name $ECS_PROJECT_NAME \
  --cluster $ECS_CLUSTER_NAME \
  --file $COMPOSEFILE \
  --ecs-params $ECS_PARAMS up \
  --region $AWS_REGION \
  --launch-type EC2 \
  --create-log-groups
  
```

Debug & Sync airflow dags code
```
# sync local code to S3 bucket
aws s3 sync . s3://bucket-superset/try-default-airflow-docker-ecs/

# sync S3 bucket specifics folders to EFS Filesystem
aws datasync start-task-execution --task-arn 'arn:aws:datasync:<your-aws-region>:<your-aws-account-id>:task/task-<task-id>'

# ssh EC2 instance and check whether the new file is mounted

# re-run airflow dag
```

Create a Load Balancer

Create a ECS service for Metabase dashboard
```
# Create a ECS Cluster with a x86 EC2 Container Instances: t3.small(2vCPU, 2GB RAM)
ecs-cli up \
  --capability-iam \
  --keypair $KEY_PAIR_NAME_ON_AWS \
  --size 1 \
  --instance-type t3.small \
  --launch-type EC2 \
  --region $AWS_REGION \
  --cluster-config $ECS_CLUSTER_CONFIG_NAME \
  --ecs-profile $ECS_PROFILE_NAME \
  --vpc $VPC_ID \
  --security-group $SECURITY_GROUP_ID \
  --subnets $SUBNET_1_ID, $SUBNET_2_ID \
  --force 
  
# Upload Task Definition for Metabase
export COMPOSEFILE=metabase-docker-compose.ecs-ec2.yml
export ECS_PROJECT_NAME=Project-ec2-metabase
export ECS_PARAMS=metabase-ecs-params.yml
ecs-cli compose --project-name $ECS_PROJECT_NAME \
  --cluster $ECS_CLUSTER_NAME \
  --file $COMPOSEFILE \
  --ecs-params $ECS_PARAMS create \
  --region $AWS_REGION \
  --launch-type EC2 \
  --create-log-groups

# Create a ECS service with Application Load Balancer
```

### Design & Code consideration
- Use selenium instead of Scrapy/Beautifulsoup4 due to batdongsan.com Cloudflare protection
- Use metabase due to its ease to share public dashboard
- Use 2 EC2 instance, a bigger one for Airflow/Postgres/Selenium, and the smaller one for Metabase.
- Use a Application Load Balancer for Metabase dashboard

### Next steps
- add feature: API for different types of user to consume data
- speed up crawling
- airflow: add Sensor 



### References
- Many many thanks: @machado-startdataengineering.com, @l1990790120-localdatastack, 



