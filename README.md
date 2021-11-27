# A scalable Web Scraper stack on AWS ECS
> insert Gifs (nhìn gif xong hiểu luôn flow đi thế nào)

"A scalable WebScraper-stack with task-orchestration and data-visualization"

Architecture: WebScraper-stack (Selenium, Airflow, PostgreSQL, Metabase) deployed on AWS ECS with a Load Balancer.
> insert image Architecture


## Objectives & Design
- Objectives: create a overview of real estate market in Saigon through a dashboard from crawled data.
- Design: Airflow on ECS to orchestrate Crawling/Cleaning/Loading, PostgreSQL for storing cleaned data, Metabase for visualization.
- [Metabase dashboard](http://vizlb-1924166062.ap-southeast-1.elb.amazonaws.com/dashboard/88e7d2ac-587d-4343-b7aa-b7a13e881839)

### Deploy Instruction
#### Deploy on Local:
- Presequisite: [Docker Desktop](https://docs.docker.com/engine/install/) with at least 6GB of RAM, [psql](https://formulae.brew.sh/formula/postgresql@13)
- Infra
- docker-compose up

#### Deploy on your AWS: 
- Presequisite
- Infra
- Config
- AWS Infrastructure Cost: $2/day ~ $60/month

### Code Walkthrough
- crawl & save to data lake
- clean data 
- load data into postgresql

### Design consideration

### Next steps
- add feature: API for different types of user to consume data
- speed up crawling


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


