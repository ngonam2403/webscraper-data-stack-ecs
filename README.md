# de_01

Mục đích tool:
- Buyer: 
-   PriceTracker: fingerprint
-   

Project này cần thể hiện:
- một pipeline hoàn chỉnh chạy tay 1 click trên infra docker: crawl -> csv -> (optional: kafka) -> storage -> dwh -> visualize -> data catalog
-   kafka để listen xem có data mới không, dù là insert hay update.
- tiếp theo: refactor để orchestrate bằng airflow (schedule, check quality, báo lỗi, v.v.)
- tiếp theo: đưa toàn bộ project lên AWS để không phải sử dụng tài nguyên localhost
- tiếp theo: refactor code để cho thấy ObjectOriented
- tiếp theo: gom nhóm bằng FINGERPRINT (phone, area, location, TenChungCu, SoPhongNgu)
- tiếp theo: theo dõi biến động giá của một số căn trong 3 
