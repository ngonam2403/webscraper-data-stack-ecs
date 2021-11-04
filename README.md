# de_01

Mục đích tool:
- Buyer: 
-   PriceTracker: fingerprint
- Business: (demo quận 3,4,5,6,7,8)
-   Thông tin đối thủ
-   Thông tin nhân sự tiềm năng
-   Overview thị trường

Project này cần thể hiện:
- một pipeline hoàn chỉnh chạy tay 1 click trên infra docker: crawl -> csv -> (optional: kafka) -> storage -> dwh -> visualize -> data catalog
-   kafka để listen xem có data mới không, dù là insert hay update.
- tiếp theo: refactor để orchestrate bằng airflow (schedule, check quality, báo lỗi, v.v.)
- tiếp theo: đưa toàn bộ project lên AWS để không phải sử dụng tài nguyên localhost
- tiếp theo: refactor code để cho thấy ObjectOriented
- tiếp theo: gom nhóm bằng FINGERPRINT (phone, area, location, TenChungCu, SoPhongNgu)
- tiếp theo: theo dõi biến động giá của một số căn trong 3 

Kiến trúc:
- Local:        python -> Data Lake (Folder)      -> Data Warehouse (PostgreSQL)      -> Visualize (Superset)
- Local Docker: ???
- On Cloud:     python -> Data Lake (S3 bucket)   -> Data Warehouse (Redshift)        -> Visualize (Superset on EMR?)
