# A scalable Web Scraper stack on AWS ECS

![This is an image](https://media.giphy.com/media/jloMAPddOFbpQYqZHI/giphy.gif)


## Architecture 
![This is an image](https://imgur.com/8q8CeTq.png)


## Objectives & Design
- Objectives: create a overview of real estate market in Saigon through a dashboard from crawled data (batdongsan.com.vn, nha.chotot.com)
- Design: Airflow on ECS to orchestrate Crawling/Cleaning/Loading, PostgreSQL for storing cleaned data, Metabase for visualization.
- A 24/7 always-on [Metabase dashboard](http://vizlb-1924166062.ap-southeast-1.elb.amazonaws.com/public/dashboard/88e7d2ac-587d-4343-b7aa-b7a13e881839), hosted on a EC2 t3.small instance with Application Load Balancer.



## Deploy Instruction
This requires you being familiar with Python3, SQL, Selenium, Docker-Compose and some AWS services.

### on Local:
- Presequisite: [Docker Desktop](https://docs.docker.com/engine/install/) with at least 6GB of RAM, [psql](https://formulae.brew.sh/formula/postgresql@13)
- [docker-compose](https://docs.docker.com/compose/compose-file/compose-file-v2/)

### on AWS: 
- Presequisite: [AWS account](https://aws.amazon.com/), AWS-CLI installed, S3, EC2, [ECS](https://docs.docker.com/cloud/ecs-compose-features/), EFS, DataSync, IAM, Cloudwatch.
- Infra
- Total AWS Infrastructure Cost: $2/day ~ $60/month

## Code Walkthrough
- Clone this repo ```$ git clone https://github.com/ngonam2403/webscraper-data-stack-ecs.git ```
- In order to make Airflow works with Selenium, we got to build a custom `Docker Image` from the `Dockerfile`. Then upload to Docker Hub https://hub.docker.com/repository/docker/ngonam24/airflow-selenium 
- Deploy on Local: 1 docker-compose file, all-in-one.
- Deploy on AWS ECS: 2 docker-compose files with 2 ecs-params files. We use 2 EC2 instances, a bigger one for Airflow/Postgres/Selenium, and the smaller one for Metabase.


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

## Design & Code consideration
- Use selenium instead of Scrapy/Beautifulsoup4 due to batdongsan.com Cloudflare protection
- Use metabase due to its ease to share public dashboard
- Use 2 EC2 instance, a bigger one for Airflow/Postgres/Selenium, and the smaller one for Metabase.
- Use a Application Load Balancer for Metabase dashboard

## Next steps
- add feature: API for different types of user to consume data
- speed up crawling
- airflow: add Sensor 
- consider more visualization tool options: Apache-Superset/Preset for more complex functions, Google Data Studio for less cost, ...
- consider more orchestration tool: Luigi
- add Observability to the stack: [Admunsen](https://github.com/amundsen-io/amundsen)/[Datahub](https://datahubproject.io/docs/quickstart), dbt, great-expectation



## References
- Many many thanks to: [@machado-startdataengineering.com](https://www.startdataengineering.com/post/data-engineering-project-for-beginners-batch-edition/), [@l1990790120-localdatastack](https://l1990790120.github.io/post/2020-04-08-local-airflow-from-scratch/), ... for inspiration & work-arounds



