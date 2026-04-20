# AI Service Guideline

Tài liệu này là kế hoạch triển khai thực chiến cho phần `AI Service` của NovaMarket.

Lưu ý về tên thư mục:
- `ai_service/` ở root repo là thư mục báo cáo và tài liệu nộp bài.
- `services/ai_service/` là source code runtime của microservice AI hiện tại.

## 1. Kết luận ngắn gọn về hướng tích hợp

Phương án bạn nêu `train trên Kaggle -> expose model qua ngrok -> gọi API vào hệ thống` chỉ nên dùng để demo tạm thời, không nên dùng làm kiến trúc chính.

Hướng hợp lý hơn cho dự án này:
- Dùng `Kaggle` hoặc `Colab` để train nếu cần GPU.
- Export artifact về local: `model_best.keras`, `scaler.pkl`, `label_encoder.pkl`.
- Nạp artifact đó trong `services/ai_service/`.
- Chạy `ai-service` bằng Docker Compose cùng các service còn lại.
- `API Gateway` giữ vai trò cổng vào duy nhất qua `/api/ai/*`.
- Frontend gọi gateway ở ba điểm: `search`, `cart`, `assistant`.

Lý do:
- ổn định hơn `ngrok`,
- dễ tái lập khi bảo vệ,
- đúng với kiến trúc microservices của repo hiện tại,
- ít rủi ro phụ thuộc Internet.

## 2. Trạng thái repo hiện tại

Repo đã có các móc tích hợp quan trọng:
- `services/ai_service/main.py`: FastAPI AI service placeholder.
- `services/api_gateway/app/main.py`: đã proxy `/api/ai/{path:path}` tới AI service.
- `services/web_frontend/src/features/assistant/pages/AssistantPage.tsx`: route `/assistant` đang là placeholder.
- `services/web_frontend/src/features/products/pages/ProductsPage.tsx`: có ô search và catalog grid.
- `services/web_frontend/src/features/cart/pages/CartPage.tsx`: đã có giỏ hàng thật và checkout flow.
- `services/product_service/`: có catalog API để lấy dữ liệu sản phẩm thật.

Điều này nghĩa là ta không phải nghĩ lại toàn bộ kiến trúc. Ta chỉ cần nâng cấp `ai-service` và thay UI placeholder bằng tính năng thật.

## 3. Mục tiêu đầu ra của phase AI Service

Khi hoàn thành phase này, hệ thống nên có:
- file `data_user500.csv` với 500 user và 8 hành vi,
- notebook hoặc script train `RNN`, `LSTM`, `biLSTM`,
- artifact `model_best`,
- Neo4j graph được nạp từ dataset và từ product catalog,
- endpoint `chat` và `recommendation`,
- recommendation hiển thị ở `search` và `cart`,
- màn hình `/assistant` thành giao diện chat riêng của NovaMarket.

## 4. Định nghĩa bài toán rõ ràng trước khi code

Đừng code ngay nếu chưa khóa bài toán.

Đề xuất bài toán:
- Input: chuỗi 8 hành vi người dùng.
- Output: nhãn `low_intent`, `medium_intent`, `high_intent`.

Tám hành vi đề xuất:
1. `search_count`
2. `product_view_count`
3. `detail_view_count`
4. `dwell_time_sec`
5. `add_wishlist_count`
6. `add_to_cart_count`
7. `remove_from_cart_count`
8. `purchase_count`

Các cột phụ nên có thêm:
- `user_id`
- `session_id`
- `last_search_keyword`
- `dominant_category`
- `target_label`

Vì sao chọn như vậy:
- đúng ngữ cảnh e-commerce,
- đủ để train mô hình tuần tự,
- đủ để dựng KB Graph,
- đủ để tạo recommendation có lý do giải thích.

## 5. Bước 1: Sinh `data_user500.csv`

Mục tiêu:
- sinh 500 dòng dữ liệu có quy luật,
- không random hoàn toàn,
- có thể học được bằng mô hình.

Cách làm:
- tạo script `generate_dataset.py` trong một workspace training riêng,
- định nghĩa danh sách category trùng với catalog hiện có:
  - `work-tech`
  - `home-living`
  - `kitchen-dining`
  - `wellness`
  - `travel-everyday`
  - `beauty-care`
- sinh `last_search_keyword` theo category,
- sinh 8 hành vi bằng phân phối hợp lý,
- tính `intent_score`,
- map score sang 3 nhãn.

Rule sinh nhãn nên có logic như sau:
- `purchase_count` và `add_to_cart_count` làm tăng mạnh `intent_score`,
- `remove_from_cart_count` làm giảm `intent_score`,
- `detail_view_count` và `dwell_time_sec` phản ánh độ quan tâm sâu,
- `search_count` và `product_view_count` phản ánh mức khám phá.

Khuyến nghị:
- giữ tỷ lệ nhãn không quá lệch, ví dụ gần `35% low`, `35% medium`, `30% high`.
- lưu file kết quả tại:
  - `ai_service/data_user500.csv` nếu bạn muốn nộp kèm tài liệu,
  - hoặc `services/ai_service/training/data_user500.csv` nếu bạn muốn để gần runtime hơn.

## 6. Bước 2: Chuẩn bị notebook train model

Nơi train:
- ưu tiên `Kaggle` hoặc `Colab` nếu máy local không có GPU hoặc cài TensorFlow khó.
- nếu local chạy được thì vẫn có thể train local.

Những gì notebook cần làm:
- đọc `data_user500.csv`,
- chọn đúng 8 cột hành vi làm input,
- encode nhãn,
- normalize dữ liệu,
- split train/validation/test,
- reshape thành `(samples, 8, 1)`,
- train 3 mô hình,
- lưu plot và bảng metrics,
- save `model_best`.

Khuyến nghị preprocessing:
- dùng `MinMaxScaler`,
- dùng `LabelEncoder`,
- `train_test_split` theo tỷ lệ `70/15/15`,
- `EarlyStopping` với `patience=8`,
- `ModelCheckpoint` để lưu best model.

## 7. Bước 3: Train và so sánh `RNN`, `LSTM`, `biLSTM`

Thiết kế tối thiểu:
- `RNN`: `SimpleRNN(64) -> Dense(32) -> Softmax`
- `LSTM`: `LSTM(64) -> Dense(32) -> Softmax`
- `biLSTM`: `Bidirectional(LSTM(64)) -> Dense(32) -> Softmax`

Metrics bắt buộc nên lưu:
- `accuracy`
- `precision`
- `recall`
- `macro_f1`
- `loss`

Plots nên xuất ra ảnh:
- `loss_accuracy_curves.png`
- `model_compare.png`
- `confusion_matrix_best.png`

Điều kiện chọn `model_best`:
- không chỉ dựa vào `accuracy`,
- ưu tiên `macro_f1` nếu class hơi lệch,
- kiểm tra overfitting qua `val_loss`,
- chọn model nào suy luận đủ nhanh cho web service.

Artifact nên export:
- `model_best.keras`
- `scaler.pkl`
- `label_encoder.pkl`
- `metrics_summary.json`

## 8. Bước 4: Đưa artifact về repo

Sau khi train xong trên Kaggle hoặc Colab:
- tải các artifact về máy,
- đặt chúng trong `services/ai_service/artifacts/`.

Cấu trúc nên có:

```text
services/ai_service/
  artifacts/
    model_best.keras
    scaler.pkl
    label_encoder.pkl
    metrics_summary.json
  main.py
  requirements.txt
```

Không nên để model chạy ở Kaggle rồi gọi từ xa bằng `ngrok` lâu dài, vì:
- rất khó reproducible,
- dễ timeout,
- URL đổi liên tục,
- không đẹp về mặt báo cáo kiến trúc.

## 9. Bước 5: Bổ sung Neo4j vào Docker Compose

Hiện `docker-compose.yml` chưa có `neo4j`, nên đây là việc bắt buộc nếu bạn muốn làm đúng yêu cầu `KB_Graph`.

Service đề xuất:

```yaml
neo4j:
  image: neo4j:5
  environment:
    NEO4J_AUTH: neo4j/novamarket123
  ports:
    - "7474:7474"
    - "7687:7687"
  volumes:
    - neo4j_data:/data
```

Biến môi trường thêm cho `ai-service`:

```yaml
AI_MODEL_PATH: /app/artifacts/model_best.keras
AI_SCALER_PATH: /app/artifacts/scaler.pkl
AI_LABEL_ENCODER_PATH: /app/artifacts/label_encoder.pkl
NEO4J_URI: bolt://neo4j:7687
NEO4J_USER: neo4j
NEO4J_PASSWORD: novamarket123
PRODUCT_SERVICE_URL: http://product-service:8010
```

## 10. Bước 6: Dựng KB Graph từ dataset và catalog thật

Đây là bước nhiều bạn hay làm hời hợt. Nếu chỉ import `User` và `Intent` thì graph quá nghèo.

Bạn nên dựng graph với ít nhất các node:
- `User`
- `Session`
- `Keyword`
- `Category`
- `Intent`
- `Product`

Quan hệ nên có:
- `HAS_SESSION`
- `SEARCHED`
- `INTERESTED_IN`
- `HAS_INTENT`
- `CONTAINS`
- `SUGGESTS`

Nguồn dữ liệu:
- `data_user500.csv` cho user behavior,
- `product-service` hoặc file seed demo hiện có cho `Category` và `Product`.

Lợi ích:
- recommendation không bị rời rạc,
- chat có thể giải thích theo category hoặc sản phẩm thật,
- ảnh Neo4j đẹp và có giá trị thuyết trình hơn.

## 11. Bước 7: Thiết kế AI Service theo lớp chức năng

Đừng nhồi toàn bộ logic vào `main.py`.

Nên tách thành các phần:
- `schemas.py`: request/response models.
- `model_loader.py`: load `model_best`, scaler, label encoder.
- `predictor.py`: nhận 8 features và trả `intent`.
- `graph_store.py`: truy vấn Neo4j.
- `recommender.py`: gộp kết quả model + graph + product service.
- `chat_service.py`: tạo response chat.
- `main.py`: chỉ giữ route layer.

Nếu chưa muốn refactor lớn ngay, ít nhất vẫn nên tổ chức logic theo các hàm riêng và để `main.py` mỏng.

## 12. Bước 8: Định nghĩa endpoint cho AI Service

Tối thiểu nên có 7 endpoint:

### `POST /api/ai/predict-intent/`

Mục đích:
- phục vụ test model độc lập.

Payload:

```json
{
  "search_count": 6,
  "product_view_count": 12,
  "detail_view_count": 5,
  "dwell_time_sec": 410,
  "add_wishlist_count": 1,
  "add_to_cart_count": 2,
  "remove_from_cart_count": 0,
  "purchase_count": 1
}
```

### `POST /api/ai/recommend/search/`

Mục đích:
- nhận từ khóa search và session,
- trả recommendation cho trang sản phẩm.

Payload:

```json
{
  "session_key": "gw_abc123",
  "query": "laptop",
  "top_k": 4
}
```

### `POST /api/ai/recommend/cart/`

Mục đích:
- nhận giỏ hàng hiện tại,
- đề xuất sản phẩm bổ sung.

Payload nên lấy từ dữ liệu cart thật của frontend:

```json
{
  "session_key": "gw_abc123",
  "items": [
    {
      "product_id": 1,
      "product_slug": "novabook-flex-13",
      "category": "Work Tech",
      "quantity": 1
    }
  ],
  "top_k": 4
}
```

### `POST /api/ai/chat/`

Mục đích:
- phục vụ giao diện `/assistant`,
- hỗ trợ hỏi đáp theo context.

Payload:

```json
{
  "session_key": "gw_abc123",
  "message": "Tôi cần đồ cho học tập và làm việc gọn nhẹ",
  "source": "assistant",
  "context": {
    "query": "laptop",
    "cart_product_slugs": ["novabook-flex-13"]
  }
}
```

### `POST /api/ai/events/`

Mục đích:
- log hành vi thực tế của user trong web app để sau này cải thiện dataset.

### `GET /api/ai/graph/status/`

Mục đích:
- kiểm tra Neo4j đã connect chưa,
- xem nhanh số lượng node và relationship sau khi import graph.

### `POST /api/ai/graph/context/`

Mục đích:
- debug riêng bước retrieve của Graph-RAG,
- truyền `query`, `cart_product_slugs`, `category_hints`,
- xem AI service lấy được evidence gì từ graph trước khi generate answer.

## 13. Bước 9: Tích hợp qua API Gateway

Repo hiện đã proxy:
- `/api/ai/{path:path}` -> `ai-service`

Vì vậy phần gateway gần như đã sẵn. Việc bạn cần làm là:
- giữ contract endpoint ổn định,
- không để frontend gọi `ai-service` trực tiếp,
- mọi request vẫn đi qua gateway để đúng kiến trúc.

Nếu cần mở rộng:
- thêm health detail cho `neo4j`,
- thêm timeout hợp lý cho route AI,
- log `x-request-id` để trace request AI khi demo.

## 14. Bước 10: Tích hợp vào frontend ở màn hình `Products`

File liên quan:
- `services/web_frontend/src/features/products/pages/ProductsPage.tsx`

Điểm móc hợp lý:
- sau khi user submit search,
- gọi thêm `/api/ai/recommend/search/`,
- hiển thị một panel kiểu `AI suggestions` bên phải hoặc phía trên grid sản phẩm.

Panel nên hiển thị:
- `predicted_intent`,
- `matched_category`,
- `2-4` sản phẩm đề xuất,
- `reason` ngắn cho từng sản phẩm.

Không nên:
- tự động override kết quả search gốc,
- làm AI thay thế hoàn toàn catalog list.

Nên làm:
- AI là lớp augmentation,
- kết quả search gốc vẫn là nguồn chính,
- AI chỉ gợi ý hoặc re-rank nhẹ.

## 15. Bước 11: Tích hợp vào frontend ở màn hình `Cart`

File liên quan:
- `services/web_frontend/src/features/cart/pages/CartPage.tsx`

Điểm móc hợp lý:
- khi cart load xong,
- hoặc sau khi add/remove/update item,
- gọi `/api/ai/recommend/cart/`.

UI nên hiển thị:
- `Frequently paired with your cart`
- `You may also need`
- `Why these items`

Đây là phần bám sát yêu cầu đề:
- hiển thị danh sách hàng khi khách hàng chọn vào giỏ hàng.

## 16. Bước 12: Thay placeholder `/assistant` bằng giao diện chat thật

File liên quan:
- `services/web_frontend/src/features/assistant/pages/AssistantPage.tsx`

Yêu cầu quan trọng của đề:
- giao diện chat với user,
- không phải giao diện kiểu ChatGPT mặc định.

Đề xuất bố cục:
- cột trái: lịch sử hội thoại,
- cột phải: suggestion cards, quick intents, category chips,
- ô input phía dưới,
- có thể thêm `Suggested prompts` như:
  - `Tư vấn đồ cho học tập`
  - `Gợi ý thêm cho giỏ hàng hiện tại`
  - `Tìm sản phẩm phù hợp ngân sách`

Điều cần giữ:
- nhìn giống một trợ lý mua sắm của NovaMarket,
- không giống bản sao của ChatGPT.

## 17. Bước 13: RAG nên làm ở mức nào cho phù hợp đồ án

Tôi khuyến nghị chia 2 mức:

### Mức 1: đủ chắc để nộp bài

Graph-RAG theo hướng deterministic:
- lấy context từ Neo4j,
- lấy product data từ product-service,
- dùng template tạo câu trả lời.

Ví dụ:
- nếu intent là `high_intent` và category là `work-tech`,
- trả lời theo form:
  - nhu cầu chính,
  - sản phẩm phù hợp,
  - lý do gợi ý,
  - sản phẩm bổ sung.

Ưu điểm:
- dễ kiểm soát,
- không cần API ngoài,
- rất ổn định khi demo.

### Mức 2: nâng cao nếu còn thời gian

Thêm LLM để paraphrase câu trả lời:
- Ollama local,
- OpenAI API,
- hoặc model bên ngoài khác.

Nhưng mức này chỉ nên làm sau khi mức 1 đã chạy ổn.

## 18. Bước 14: Kiểm thử và minh chứng cho báo cáo

Bạn cần chuẩn bị các loại minh chứng sau:
- 20 dòng đầu của `data_user500.csv`,
- ảnh loss/accuracy curves,
- bảng metrics 3 mô hình,
- confusion matrix mô hình tốt nhất,
- ảnh import Neo4j hoặc query table,
- ảnh graph visualization,
- ảnh recommendation ở `Products`,
- ảnh recommendation ở `Cart`,
- ảnh giao diện chat `/assistant`.

Nếu thiếu các ảnh này, báo cáo sẽ bị yếu dù code có chạy.

## 19. Thứ tự làm thực tế tôi khuyên bạn

Nếu làm theo thứ tự tối ưu, hãy đi như sau:

1. Sinh `data_user500.csv`.
2. Train `RNN`, `LSTM`, `biLSTM` trên Kaggle/Colab.
3. Chốt `model_best` và export artifact.
4. Thêm `neo4j` vào Compose.
5. Nạp graph từ dataset và catalog thật.
6. Nâng cấp `services/ai_service/` thành service thật.
7. Tích hợp search recommendation.
8. Tích hợp cart recommendation.
9. Thay màn hình `/assistant`.
10. Chụp ảnh và điền kết quả vào `aiservice.tex`.

Đây là thứ tự ít rủi ro nhất vì:
- bạn có số liệu model trước,
- có graph trước,
- sau đó mới gắn UI,
- tránh tình trạng giao diện xong nhưng backend AI chưa chốt.

## 20. Rủi ro cần tránh

Những lỗi tôi thấy dễ gặp nhất:
- chọn bài toán dự đoán không rõ ràng,
- dữ liệu synthetic sinh ngẫu nhiên quá mức nên model không học được gì,
- graph quá nghèo nên RAG chỉ là hình thức,
- phụ thuộc `ngrok` làm demo fail,
- cố gắng làm chat kiểu LLM phức tạp quá sớm,
- tích hợp AI trực tiếp vào frontend mà bỏ qua gateway.

## 21. Chốt kiến trúc nên dùng

Kiến trúc tôi đề xuất cho dự án này là:

```text
Kaggle/Colab (training only)
    -> export model_best + scaler + label_encoder
    -> services/ai_service/artifacts/
React frontend
    -> API Gateway (/api/ai/*)
    -> FastAPI ai-service
        -> model_best
        -> Neo4j KB Graph
        -> product-service
```

Đây là hướng hợp lý hơn `ngrok API`, bảo vệ dễ hơn, và khớp hẳn với kiến trúc microservices bạn đã xây.

## 22. Gợi ý bước tiếp theo

Sau tài liệu này, bước tiếp theo nên là:
- tôi giúp bạn sinh luôn `data_user500.csv`,
- scaffold notebook train `RNN/LSTM/biLSTM`,
- nâng cấp `services/ai_service/` thành API thật,
- sau đó gắn thẳng vào `ProductsPage`, `CartPage`, `AssistantPage`.

Đó là chuỗi triển khai đúng nhất nếu mục tiêu của bạn là vừa nộp được báo cáo, vừa có demo chạy thật.

## 23. Trạng thái hiện tại sau khi đã có artifact

Sau khi bạn train xong trên Kaggle và copy artifact về:

```text
services/ai_service/artifacts/
  model_best.keras
  scaler.pkl
  label_encoder.pkl
  metrics_summary.json
```

service hiện đã được nâng cấp để:
- tự load artifact từ thư mục `services/ai_service/artifacts/`,
- dùng `model_best.keras` để suy luận `intent`,
- fallback về heuristic nếu artifact hỏng hoặc thiếu dependency,
- expose trạng thái model qua `/health`.

Điểm kỹ thuật chính:
- `services/ai_service/model_loader.py`: load model, scaler, label encoder, metrics.
- `services/ai_service/intelligence.py`: dùng artifact-backed inference trước, heuristic sau.
- `services/ai_service/main.py`: `/health` đã trả `model.backend`, `model.ready`, `best_model`.

## 24. Những gì bạn nên làm tiếp theo ngay bây giờ

Thứ tự đúng sau khi đã có artifact là:

1. Build lại hoặc chạy lại `ai-service`.
2. Kiểm tra `/health` xem `backend` đã là `artifact_model` chưa.
3. Test các endpoint AI chính.
4. Chụp ảnh kết quả để đưa vào báo cáo.
5. Sau đó mới sang `Neo4j`, `KB_Graph`, `RAG`.

### Bước 1: kiểm tra health

Khi service chạy đúng, `/health` nên trả gần giống:

```json
{
  "status": "ok",
  "service": "novamarket-ai-service",
  "dataset_loaded": 500,
  "model": {
    "backend": "artifact_model",
    "ready": true,
    "best_model": "RNN"
  }
}
```

Nếu `backend` vẫn là `heuristic_fallback` thì cần kiểm tra:
- artifact có đúng tên file không,
- `tensorflow`, `joblib`, `scikit-learn` đã được cài trong container chưa,
- đường dẫn artifact trong service có đúng không.

### Bước 2: test các endpoint

Tối thiểu nên test:

- `POST /api/ai/predict-intent/`
- `POST /api/ai/recommend/search/`
- `POST /api/ai/recommend/cart/`
- `POST /api/ai/chat/`

Kỳ vọng:
- `predict-intent` trả label thật từ model,
- `search` có recommendation ở `/products`,
- `cart` có add-on suggestion ở `/cart`,
- `assistant` trả hội thoại và shortlist sản phẩm.

### Bước 3: kiểm tra UI

Bạn nên demo nhanh ba điểm:
- `/products` với query như `laptop`, `yoga`, `travel bag`
- `/cart` sau khi thêm 1-2 sản phẩm
- `/assistant` với prompt kiểu:
  - `Suggest products for study and portable work`
  - `Recommend add-ons for my cart`
  - `Find products for a calm home routine`

## 25. Bước tiếp theo sau khi artifact integration đã ổn

Khi model inference đã chạy ổn, phần tiếp theo nên là:

### 25.1. Hoàn thiện báo cáo AI

Bạn cần lấy thêm từ Kaggle:
- `metrics_summary.json`
- ảnh `loss_accuracy_curves.png`
- ảnh `model_compare.png`
- ảnh `confusion_matrix_best.png`

Rồi chèn vào:
- `ai_service/figures/`
- cập nhật lại `aiservice.tex`

### 25.2. Thêm Neo4j vào hệ thống

Đây là bước tiếp theo có giá trị nhất về mặt đề bài.

Bạn nên làm:
- thêm `neo4j` vào `docker-compose.yml`,
- tạo script import từ `data_user500.csv`,
- import thêm `Category` và `Product` từ catalog thật,
- chụp ảnh graph để đưa vào báo cáo.

### 25.3. Làm RAG theo hướng thực dụng

Tôi khuyến nghị:
- không nhảy ngay vào LLM phức tạp,
- trước hết làm `Graph-RAG deterministic`,
- tức là:
  - truy vấn Neo4j,
  - lấy category/product liên quan,
  - rồi dùng template sinh câu trả lời.

Như vậy:
- dễ kiểm soát,
- dễ debug,
- rất phù hợp với deadline đồ án.

### 25.4. Chốt demo script

Luồng demo tốt nhất sau bước này là:

1. Mở `/products`, search một từ khóa.
2. Chỉ AI suggestion panel.
3. Add sản phẩm vào cart.
4. Mở `/cart`, chỉ AI cart suggestions.
5. Mở `/assistant`, hỏi một câu gợi ý sản phẩm.
6. Mở `/health` hoặc gateway dashboard để chứng minh service AI đang chạy bằng model thật.

Nếu bạn giữ được flow này ổn định, phần còn lại của AI service sẽ chủ yếu là nâng chất lượng báo cáo và hoàn thiện `Neo4j/RAG`.

## 26. Trạng thái mới: KB_Graph, Neo4j và Graph-RAG đã được scaffold

Hiện tại codebase đã được đẩy thêm một bước:

- `docker-compose.yml` đã có service `neo4j`.
- `services/ai_service/graph_store.py` đã có lớp làm việc với Neo4j.
- `services/ai_service/rebuild_kb_graph.py` là CLI để import lại graph thủ công.
- `services/ai_service/main.py` đã có endpoint:
  - `POST /api/ai/graph/rebuild/`
- `search`, `cart`, `chat` đã được nối sang graph retrieval trước khi tạo câu trả lời.

Nói ngắn gọn:
- model artifact quyết định `intent`,
- Neo4j cung cấp `graph context`,
- AI service dùng cả hai để tạo recommendation và chat response.

Đây chính là hướng `Graph-RAG deterministic` phù hợp nhất cho đồ án này.

## 27. Cách chạy phần Neo4j và KB_Graph

### 27.1. Build lại stack

Vì `services/ai_service/requirements.txt` và `docker-compose.yml` đã đổi, bạn cần build lại:

```bash
docker compose down
docker compose up --build
```

Nếu chỉ muốn chạy riêng AI stack:

```bash
docker compose up --build neo4j ai-service api-gateway product-service web-frontend
```

### 27.2. Kiểm tra Neo4j

Sau khi stack lên:
- Neo4j Browser: `http://localhost:7474`
- user: `neo4j`
- password: `novamarket123`

### 27.3. Kiểm tra AI health

Bạn nên kiểm tra:

```bash
curl http://localhost:8001/health
```

Khi mọi thứ đã đúng, phần `graph` trong response nên là:

```json
{
  "backend": "neo4j",
  "ready": true
}
```

Sau đó kiểm tra chi tiết graph:

```bash
curl http://localhost:8001/api/ai/graph/status/
```

Khi import đã thành công, response nên có thêm:
- `node_counts`
- `relationship_counts`

Ví dụ:

```json
{
  "backend": "neo4j",
  "ready": true,
  "node_counts": {
    "Category": 6,
    "Intent": 3,
    "Keyword": 60,
    "Product": 12,
    "Session": 500,
    "User": 500
  }
}
```

### 27.4. Rebuild graph nếu cần

Có hai cách:

Qua API:

```bash
curl -X POST http://localhost:8001/api/ai/graph/rebuild/
```

Qua CLI trong service:

```bash
cd services/ai_service
python3 rebuild_kb_graph.py
```

### 27.5. Debug retrieval riêng trước khi test UI

Nếu muốn chắc phần Graph-RAG đã hoạt động trước khi mở frontend, hãy gọi:

```bash
curl -X POST http://localhost:8001/api/ai/graph/context/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "laptop for study and portable work",
    "cart_product_slugs": ["novabook-flex-13"],
    "category_hints": ["work-tech"],
    "top_k": 4
  }'
```

Nếu đúng, response sẽ có:
- `backend: neo4j`
- `matched_category`
- `evidence`
- `retrieved_product_names`
- `observed_intents`

## 28. Cấu trúc KB_Graph hiện tại

Graph hiện tại được import từ:
- `data_user500.csv`
- `PRODUCT_KNOWLEDGE`
- `CATEGORY_KNOWLEDGE`

Các node chính:
- `User`
- `Session`
- `Keyword`
- `Intent`
- `Category`
- `Product`

Các quan hệ chính:
- `HAS_SESSION`
- `SEARCHED`
- `INTERESTED_IN`
- `HAS_INTENT`
- `RELATES_TO`
- `CONTAINS`
- `COMPLEMENTS`
- `RELATED_TO`

Điểm mạnh của cách này:
- có graph đủ giàu để chụp ảnh Neo4j cho báo cáo,
- có retrieval context thật cho phần chat,
- không phải phụ thuộc LLM ngoài ngay từ đầu.

## 29. Graph-RAG hiện đang hoạt động như thế nào

### 29.1. Search recommendation

Luồng xử lý:
- frontend gửi query search,
- AI service dùng graph tìm category phù hợp từ `Keyword -> Category`,
- lấy product slugs từ `Category -> Product`,
- dùng model để dự đoán intent,
- trả shortlist sản phẩm có explanation.

### 29.2. Cart recommendation

Luồng xử lý:
- frontend gửi cart slugs,
- graph dùng `Product -> COMPLEMENTS -> Product`,
- lấy thêm `RELATED_TO` categories nếu cần,
- service xếp hạng add-on products,
- trả lời theo ngữ cảnh giỏ hàng.

### 29.3. Assistant chat

Luồng xử lý:
- nhận message và cart context,
- graph tìm category mạnh nhất,
- lấy observed intents trong graph,
- lấy complement products và category products,
- service sinh câu trả lời dạng template có nhúng evidence từ graph.

Đây là `RAG` theo nghĩa:
- có bước `retrieve` từ graph,
- có bước `augment` bằng product metadata,
- có bước `generate` response.

Từ phiên bản code hiện tại, phần response của `search`, `cart`, `chat` còn trả thêm:
- `retrieval_context.backend`
- `retrieval_context.evidence`
- `retrieval_context.related_categories`
- `retrieval_context.observed_intents`
- `retrieval_context.retrieved_product_names`

Điểm này rất quan trọng vì:
- frontend có thể hiển thị trực tiếp bằng chứng Graph-RAG,
- bạn dễ chứng minh đây không phải chỉ là rule-based text ngầm,
- việc debug demo khi bảo vệ sẽ nhanh hơn nhiều.

## 30. Những gì bạn nên làm tiếp theo ngay sau bước này

Sau khi Neo4j chạy được, bạn nên làm theo đúng thứ tự:

1. Mở Neo4j Browser và chụp ảnh graph.
2. Gọi `POST /api/ai/graph/rebuild/` và chụp response.
3. Gọi `GET /api/ai/graph/status/` để kiểm tra node và relationship counts.
4. Gọi `POST /api/ai/graph/context/` với 1 query mẫu để chụp evidence retrieval.
5. Test `/products`, `/cart`, `/assistant` khi stack chạy thật.
6. Chụp lại các UI có AI panel và chat, trong đó panel phải hiện `Graph-RAG active` nếu Neo4j đã sẵn sàng.
7. Sau đó mới quay lại hoàn thiện báo cáo `aiservice.tex`.

## 31. Luồng chạy thực tế tôi khuyên bạn làm ngay bây giờ

Đây là thứ tự ít rủi ro nhất sau khi đã có đủ artifact trong `services/ai_service/artifacts/`:

1. Chạy `docker compose down`.
2. Chạy `docker compose up --build`.
3. Đợi `product-service`, `ai-service`, `neo4j`, `api-gateway`, `web-frontend` lên ổn định.
4. Kiểm tra `http://localhost:8001/health`.
5. Kiểm tra `http://localhost:8001/api/ai/graph/status/`.
6. Nếu graph chưa có dữ liệu hoặc `node_counts` rỗng, gọi `POST /api/ai/graph/rebuild/`.
7. Mở `http://localhost:7474` để kiểm tra Neo4j Browser.
8. Mở `http://localhost:8080/products?q=laptop` để xem AI search recommendation.
9. Add sản phẩm vào cart rồi mở `http://localhost:8080/cart`.
10. Mở `http://localhost:8080/assistant` và gửi prompt mẫu.

Prompt nên dùng để demo:
- `Suggest products for study and portable work`
- `Recommend add-ons for my cart`
- `Find products for a calm home routine`
- `Help me choose between wellness and travel essentials`

## 32. Khi nào mới nên quay lại làm báo cáo

Chỉ quay lại `aiservice.tex` khi 4 thứ sau đều đã ổn:
- `/health` báo `artifact_model` và `neo4j`.
- `/api/ai/graph/status/` có `node_counts` và `relationship_counts`.
- `Products`, `Cart`, `Assistant` đều hiện recommendation thật.
- frontend panel hiện được bằng chứng `retrieval_context`.

Lúc đó phần báo cáo sẽ rất dễ viết vì bạn đã có:
- ảnh training,
- ảnh artifact-backed AI,
- ảnh Neo4j graph,
- ảnh Graph-RAG evidence,
- ảnh UI tích hợp end-to-end.

## 33. Checklist chụp ảnh cho báo cáo AI

Bạn nên chuẩn bị đủ các ảnh sau:
- ảnh 20 dòng đầu của `data_user500.csv`
- ảnh metric 3 mô hình
- ảnh loss curves
- ảnh model comparison
- ảnh confusion matrix
- ảnh Neo4j Browser đăng nhập và schema graph
- ảnh graph visualization có đủ `User`, `Session`, `Category`, `Product`, `Intent`
- ảnh `/products` có AI suggestions
- ảnh `/cart` có AI suggestions
- ảnh `/assistant` có chat và shortlist sản phẩm

Nếu đủ bộ ảnh này, phần báo cáo sẽ rất chắc vì nó phản ánh đúng toàn bộ pipeline:

```text
Dataset -> Train model -> Export artifact -> AI service -> Neo4j KB_Graph -> Graph-RAG -> UI integration
```
