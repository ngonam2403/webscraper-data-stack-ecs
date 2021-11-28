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
ecs-cli configure profile --access-key $AWS_ACCESS_KEY_ID --secret-key $AWS_SECRET_ACCESS_KEY --profile-name $ECS_PROFILE_NAME

# Create a cluster configuration
ecs-cli configure --cluster $ECS_CLUSTER_NAME \
  --default-launch-type EC2 \
  --config-name $ECS_CLUSTER_CONFIG_NAME \
  --region $AWS_REGION

# Creating a Cluster with a x86 EC2 Container Instances: 2vCPU, 4GB RAM.
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


```

Mount your EFS filesystem
[ssh into your EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html)
[mount your EFS filesystem to EC2](https://docs.aws.amazon.com/efs/latest/ug/wt1-test.html)
```
mkdir -p efs
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport fs-05a24862a3f53b475.efs.ap-southeast-1.amazonaws.com:/ efs
```

### Design & Code consideration
- Use selenium instead of Scrapy/Beautifulsoup4 due to batdongsan.com Cloudflare protection
- Use metabase due to its ease to share public dashboard
- Use 2 EC2 instance, a bigger one for Airflow/Postgres/Selenium, and the smaller one for Metabase.

### Next steps
- add feature: API for different types of user to consume data
- speed up crawling
- airflow: add Sensor 



### References
- Many many thanks: @machado-startdataengineering.com, @l1990790120-localdatastack, 


## Archived
1. Mục đích tool:
- Buyer: 
-   PriceTracker: fingerprint
- Business: (demo quận 3,4,5,6,7,8)
-   Thông tin đối thủ
-   Thông tin nhân sự tiềm năng
-   Overview thị trường

2. Project này cần thể hiện:
- một pipeline hoàn chỉnh chạy tay 1 click trên infra docker: crawl -> csv -> (optional: kafka) -> storage -> dwh -> visualize -> data catalog -> FastAPI để các bên khác sử dụng dữ liệu
-   kafka để listen xem có data mới không, dù là insert hay update.
- tiếp theo: refactor để orchestrate bằng airflow (schedule, check quality, báo lỗi, v.v.)
- tiếp theo: đưa toàn bộ project lên AWS để không phải sử dụng tài nguyên localhost
- tiếp theo: refactor code để cho thấy ObjectOriented
- tiếp theo: gom nhóm bằng FINGERPRINT (phone, area, location, TenChungCu, SoPhongNgu)
- tiếp theo: theo dõi biến động giá của một số căn trong 3 

3. Kiến trúc:
- Local:        python -> Data Lake (Folder)      -> Data Warehouse (PostgreSQL)      -> Visualize (Superset)
- Local Docker: ???
- On Cloud:     python -> Data Lake (S3 bucket)   -> Data Warehouse (Redshift)        -> Visualize (Superset on EMR?)


4. Run trên máy của bạn:


