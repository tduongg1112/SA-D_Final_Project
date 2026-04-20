# Plan Triển Khai Tiểu Luận: NovaMarket Multi-category E-commerce theo DDD + AI + API Gateway

## 1. Mục tiêu tổng thể
- Xây dựng một tiểu luận môn học có logic chặt chẽ từ `phân tích yêu cầu -> phân rã domain theo DDD -> thiết kế kiến trúc microservice -> thiết kế AI service -> hiện thực code`.
- Khởi đầu từ tinh thần bài `TechStore E-commerce` cũ, nhưng mở rộng thành hệ `multi-category e-commerce` với ít nhất `12 sản phẩm khác nhau`, đồng thời nâng cấp toàn bộ tư duy thiết kế theo hướng `DDD-first`.
- Bám sát yêu cầu của giảng viên là sử dụng `Django` trong phần hiện thực, nhưng vẫn đảm bảo giao diện và trải nghiệm đủ hiện đại để demo tốt.
- Bổ sung `API Gateway` như một thành phần kiến trúc bắt buộc, đóng vai trò cổng vào duy nhất nhận request và định tuyến tới đúng service/module.

## 2. Cách hiểu chính xác đề bài
- `Chương 1` là phần nền tảng học thuật:
  - Từ Monolith sang Microservices.
  - Thiết kế microservices theo DDD.
  - Case study `Healthcare` dùng để minh họa cách phân rã domain, không phải phần code chính.
- `Chương 2` trở đi là trọng tâm của tiểu luận:
  - Phân tích yêu cầu hệ `E-commerce`.
  - Xác định actor, domain, nghiệp vụ.
  - Phân rã bounded contexts theo DDD.
- `Chương 3` là phần kiến trúc:
  - Thiết kế từng service.
  - Thiết kế cách các service kết nối với nhau.
  - Bổ sung rõ `API Gateway` là entry point của toàn hệ thống.
- `Chương 4` là phần `AI Service`:
  - Phân tích hành vi khách hàng.
  - Knowledge Base.
  - RAG.
  - Nếu có Deep Learning thì chỉ nên làm ở mức MVP dễ giải thích, không chọn hướng nặng khó demo.
- `Chương 5` là phần code:
  - Hiện thực hệ thống đủ để chứng minh được kiến trúc, domain và AI service.

## 3. Kiến trúc đích của hệ thống

### 3.1. Bounded Contexts / Service logic
- `Identity & Access`
  - Quản lý tài khoản `Admin`, `Staff`, `Customer`.
  - Authentication, authorization, hồ sơ người dùng.
- `Product`
  - Product, Category, brand, description, price, inventory snapshot.
  - Tìm kiếm, lọc, xem chi tiết sản phẩm.
- `Cart`
  - Giỏ hàng của khách, thêm/xóa/cập nhật số lượng, tính tạm tính.
- `Ordering`
  - Checkout, tạo đơn hàng, trạng thái đơn hàng, lịch sử đơn.
- `Payment`
  - Mô phỏng thanh toán, lưu trạng thái pending/success/failed.
- `Shipping`
  - Địa chỉ nhận hàng, phương thức giao hàng, trạng thái vận chuyển.
- `AI Assistant / AI Insight`
  - Gợi ý sản phẩm.
  - Hỏi đáp theo knowledge base.
  - Phân tích hành vi khách hàng ở mức cơ bản để phục vụ tư vấn.

### 3.2. API Gateway
- `API Gateway` là cổng vào duy nhất của hệ thống.
- Chức năng chính:
  - Nhận request từ Browser hoặc client.
  - Định tuyến request đến service phù hợp.
  - Ẩn topology nội bộ của hệ thống.
  - Chuẩn hóa URL, response headers, lỗi truy cập cơ bản.
  - Có thể là nơi áp dụng auth forwarding, rate limiting hoặc logging ở mức đơn giản.
- Phương án phù hợp cho đồ án:
  - Dùng `API Gateway` dạng service có code riêng ở lớp biên.
  - Route dự kiến:
    - `/` hoặc `/app/` -> Django Web App.
    - `/api/products/` -> Product module/service.
    - `/api/cart/` -> Cart module/service.
    - `/api/orders/` -> Ordering module/service.
    - `/api/payments/` -> Payment module/service.
    - `/api/shipping/` -> Shipping module/service.
    - `/api/ai/` -> AI service.
- Trong giai đoạn MVP, dù core vẫn có thể triển khai dưới dạng `DDD-aligned modular monolith`, `API Gateway` vẫn tồn tại ở lớp ngoài để đảm bảo đúng yêu cầu môn học và dễ tiến hóa thành microservices thực sự sau này.

### 3.3. Stack triển khai đề xuất
- `Backend core`: Django.
- `Database`: PostgreSQL.
- `Frontend`: Django Templates + `Tailwind CSS` + `HTMX` hoặc `Alpine.js`.
- `AI service`: FastAPI hoặc Python service riêng.
- `Gateway`: FastAPI gateway service.
- `Containerization`: Docker Compose.

## 4. Nguyên tắc triển khai khi bắt đầu coding
- Trước phase coding phải đọc `CLAUDE.md` và áp dụng các nguyên tắc sau:
  - Không code khi chưa chốt rõ mục tiêu và success criteria.
  - Ưu tiên giải pháp đơn giản nhất đáp ứng yêu cầu.
  - Chỉ thay đổi đúng phần cần thay đổi.
  - Mỗi phase implement phải có cách verify rõ ràng.
- Áp dụng thành checklist làm việc:
  1. Chốt đầu ra của phase.
  2. Chia bước triển khai nhỏ.
  3. Xác định cách verify từng bước.
  4. Chỉ code phần tối thiểu cần thiết để đạt mục tiêu.

## 5. Kế hoạch implement theo phase

### Phase 1. Chuẩn hóa yêu cầu và phạm vi
- Đầu ra:
  - Viết lại `yêu_cầu_đề_bài.txt` thành bản diễn giải đầy đủ hơn.
  - Chốt ranh giới giữa phần lý thuyết và phần hiện thực.
  - Chốt danh sách actor, domain và luồng nghiệp vụ chính.
- Verify:
  - Tài liệu phải trả lời được các câu hỏi: làm gì, làm đến đâu, vì sao chọn hướng này.

### Phase 2. Phân tích domain theo DDD
- Đầu ra:
  - Xác định bounded contexts của hệ `NovaMarket`.
  - Xác định aggregate, entity, value object ở mức đủ dùng.
  - Vẽ hoặc mô tả context map.
- Trọng tâm:
  - Không tách service theo loại sản phẩm như bài cũ.
  - Tách theo nghiệp vụ và ownership dữ liệu.
- Verify:
  - Mỗi domain phải có trách nhiệm rõ.
  - Không có dữ liệu cốt lõi bị ownership chồng chéo.

### Phase 3. Thiết kế kiến trúc hệ thống
- Đầu ra:
  - Sơ đồ tổng thể hệ thống.
  - Sơ đồ các service/module.
  - Thiết kế `API Gateway`.
  - Mô tả giao tiếp giữa các service.
- Quyết định kiến trúc:
  - Gateway ở ngoài cùng.
  - Django là core app cho business.
  - AI service là thành phần có thể tách riêng.
- Verify:
  - Có thể mô tả rõ một request đi từ client qua gateway vào các service như thế nào.

### Phase 4. Thiết kế dữ liệu và interface
- Đầu ra:
  - Data model mức khái niệm cho `User`, `Product`, `Category`, `Cart`, `Order`, `Payment`, `Shipping`.
  - Danh sách API nội bộ/chủ đạo.
  - Hợp đồng input/output cho AI service.
- Verify:
  - Một luồng `browse -> cart -> checkout -> payment -> shipping` phải mô tả được bằng dữ liệu và API.

### Phase 5. Chuẩn bị codebase
- Đầu ra:
  - Skeleton dự án `Django + PostgreSQL + code-based API Gateway + AI service`.
  - Cấu trúc thư mục phản ánh bounded contexts.
  - Docker Compose và cấu hình gateway ở mức tối thiểu.
- Nguyên tắc:
  - Chỉ tạo cấu trúc tối thiểu để triển khai các flow chính.
  - Không over-engineer từ đầu.
- Verify:
  - Hệ thống phải boot được local bằng một lệnh chính.

### Phase 6. Implement core nghiệp vụ
- Thứ tự triển khai:
  1. `Identity & Access`
  2. `Product`
  3. `Cart`
  4. `Ordering`
  5. `Payment`
  6. `Shipping`
- Mục tiêu:
  - Hoàn thành một luồng mua hàng end-to-end đủ demo.
- Verify:
  - Customer có thể duyệt sản phẩm, thêm giỏ, đặt hàng, thanh toán mô phỏng và xem trạng thái đơn.

### Phase 7. Implement AI service
- Đầu ra:
  - Knowledge Base cho tư vấn sản phẩm.
  - API hỏi đáp cơ bản.
  - Phân tích hành vi khách hàng ở mức đơn giản, dễ trình bày.
- Hướng MVP:
  - Query theo ngữ cảnh sản phẩm.
  - Gợi ý sản phẩm theo nhu cầu.
  - Fallback khi AI không trả lời được.
- Verify:
  - Từ giao diện khách hàng gọi được AI service qua `API Gateway`.

### Phase 8. UI, testing, báo cáo, demo
- Đầu ra:
  - Giao diện frontend sạch, hiện đại, dễ demo.
  - Test cho các luồng nghiệp vụ chính.
  - Tài liệu báo cáo bám đúng cấu trúc 5 chương.
  - Demo script để thuyết trình.
- Verify:
  - Demo được các flow chính trong thời gian ngắn.
  - Kiến trúc trình bày khớp với code hiện thực.

## 6. Luồng demo tối thiểu phải có
- Customer truy cập hệ thống qua `API Gateway`.
- Customer xem danh mục sản phẩm và chi tiết sản phẩm.
- Customer thêm sản phẩm vào giỏ hàng.
- Customer thực hiện checkout.
- Hệ thống tạo order, xử lý payment mô phỏng và shipping info.
- Customer hỏi AI để được gợi ý sản phẩm.
- Staff hoặc Admin đăng nhập để xem và quản lý dữ liệu liên quan.

## 7. Tiêu chí hoàn thành
- Tài liệu phải thể hiện được tư duy `DDD + Microservices`.
- Kiến trúc phải có `API Gateway` rõ ràng.
- Code phải bám sát thiết kế chứ không tách rời báo cáo.
- Có ít nhất một flow nghiệp vụ end-to-end và một flow AI hoạt động được.
- Giao diện phải đủ sạch, dễ nhìn, không mang cảm giác demo sơ sài.

## 8. Ghi chú về bài kiểm tra cũ
- `Kiemtra1_Overview.md` chỉ được dùng như tài liệu tham khảo để giữ tinh thần bài cũ, không ràng buộc phạm vi sản phẩm của bản hiện tại.
- Không kế thừa nguyên trạng cách chia service cũ.
- Bản tiểu luận này phải được xem là một phiên bản nâng cấp:
  - đúng hơn về DDD,
  - rõ hơn về bounded contexts,
  - có `API Gateway`,
  - có kiến trúc nhất quán hơn giữa báo cáo và code.

## 9. Trạng thái triển khai hiện tại
- `Phase 1` đến `Phase 5`: đã hoàn thành ở mức triển khai thực tế.
- `Phase 6`: đang hoạt động cho flow chính `product -> cart -> checkout -> payment -> shipping`.
- `Phase 7`: tạm hoãn phần AI theo quyết định hiện tại.
- `Phase 8`: đang trong giai đoạn hoàn thiện UI, kiểm thử, và siết lại trải nghiệm demo.

### Những phần đã chạy được
- `API Gateway` có service riêng, routing riêng, health check tổng hợp, và giao diện gateway riêng.
- Các bounded contexts chính đã được tách thành các service độc lập:
  - `product-service`
  - `cart-service`
  - `ordering-service`
  - `payment-service`
  - `shipping-service`
  - `commerce-service`
- Dữ liệu demo đã được mở rộng theo hướng `multi-category marketplace` với `12 sản phẩm` thuộc nhiều nhóm hàng khác nhau.
- Login qua gateway đã hoạt động ổn.
- Add-to-cart qua gateway đã hoạt động ổn.
- Checkout qua gateway đã tạo order và clear cart thành công.

### Những phần đang tiếp tục hoàn thiện
- Tinh chỉnh UI theo đúng style sidebar + analytics sạch và thoáng hơn.
- Mở rộng test coverage cho các flow nghiệp vụ chính.
- Dọn nốt các container cũ không còn thuộc kiến trúc compose hiện tại.
- Rà lại toàn bộ copy, layout, spacing và độ nhất quán giữa các màn hình.
