# UI Plan: NovaMarket Frontend Rebuild

## 1. Mục tiêu của lần rebuild này

- Xây lại frontend từ đầu theo tiêu chuẩn product UI nghiêm túc, không vá tiếp lớp template cũ.
- Chuyển định hướng từ `Django templates + CSS/HTML thuần` sang một stack frontend chuyên nghiệp hơn, dễ scale và dễ giữ độ nhất quán.
- Bám theo tinh thần của 2 ảnh mẫu:
  - sáng màu
  - hiện đại
  - grid chặt, spacing chuẩn
  - button bo đẹp, rõ hierarchy
  - sidebar dọc rõ ràng
  - nhiều icon nhưng không rối
  - typography gọn, sạch, product-grade
- Giữ nguyên backend contract hiện có của hệ thống:
  - `product-service`
  - `cart-service`
  - `ordering-service`
  - `payment-service`
  - `shipping-service`
  - `api-gateway`
  - `ai-service` để dành cho phase sau

## 2. Quyết định công nghệ

### 2.1. Quyết định chính

Frontend mới sẽ **không tiếp tục dùng HTML/CSS thuần làm lớp UI chính**.

Stack đề xuất để build lại:

- `React 19`
- `TypeScript`
- `Vite`
- `Tailwind CSS v4`
- `React Router`
- `TanStack Query`
- `shadcn/ui`
- `Radix UI`
- `Lucide React`
- `clsx` + `tailwind-merge`
- `Zod`

### 2.2. Vì sao đổi stack

Lý do kỹ thuật và thực dụng:

- UI hiện đại cần hệ thống component rõ ràng, trong khi template thuần rất dễ trượt sang copy-paste và lệch layout.
- Tailwind giúp khóa spacing, radius, sizing, state và responsive bằng token thống nhất.
- React phù hợp hơn để xây:
  - app shell
  - sidebar dọc
  - card system
  - dashboard/grid đồng nhất
  - state UI rõ ràng cho cart, filters, loading, empty state
- `shadcn/ui + Radix` cho accessibility tốt hơn và tiết kiệm thời gian làm component nền.
- `TanStack Query` phù hợp với hiện trạng kiến trúc vì frontend sẽ đọc dữ liệu qua gateway/API service.

### 2.3. Kiến trúc frontend đề xuất

Khuyến nghị:

- Tạo một frontend app riêng, ví dụ:
  - `services/web_frontend/`
- API Gateway sẽ là entry point thống nhất:
  - `/` hoặc `/app/*` -> frontend app
  - `/api/*` -> business services
  - `/gateway/*` -> gateway/operator routes

Lợi ích:

- frontend tách khỏi Django template rendering
- dễ scale và test
- dễ đưa AI UI vào sau
- đúng tinh thần microservices + gateway hơn

### 2.4. Vai trò còn lại của commerce-service

Trong phase UI rebuild:

- `commerce-service` không còn là nơi render UI chính
- có thể giữ vai trò transitional/BFF nếu cần trong một giai đoạn ngắn
- về đích, frontend React nên đọc trực tiếp qua gateway thay vì bám template server-rendered

## 3. Tham chiếu thị giác từ 2 ảnh mẫu

### 3.1. Tinh thần tổng thể

Hai ảnh mẫu gợi ra 2 lớp visual cần kết hợp:

- Ảnh 1:
  - app shell có `sidebar dọc`
  - grid alignment cực chặt
  - spacing 4px rule
  - typography và icon được kiểm soát chính xác
- Ảnh 2:
  - bề mặt sáng, sạch
  - card bo lớn
  - hero sáng màu
  - button nổi bật nhưng không thô
  - layout nhìn như SaaS product thực sự

NovaMarket UI mới sẽ lấy:

- `App shell + sidebar discipline` từ ảnh 1
- `Card tone + modern cleanliness + CTA quality` từ ảnh 2

### 3.2. Nguyên tắc bắt buộc

- Mọi spacing theo bội số `4px`, không ngoại lệ.
- Mọi icon cùng một family, cùng stroke, cùng khung chứa.
- Mọi grid phải có cột và row logic rõ, không dựng theo cảm tính.
- Các card cùng loại phải có cùng chiều cao header, body spacing và action row.
- Text baseline phải đồng đều:
  - heading
  - description
  - metadata
  - badge
- Không dùng màu ngẫu hứng hoặc gradient rối.
- Không dùng shadow nặng.
- Không để button/phần tử interactive có chiều cao lẫn lộn.
- Không để sidebar, toolbar, card title, badge, table row lệch nhau theo pixel.

## 4. Design language mới

### 4.1. Phong cách hình ảnh

Mục tiêu cảm giác:

- bright
- premium
- calm
- product-grade
- clean but not empty
- minimal nhưng không vô hồn

Từ khóa visual:

- white canvas
- soft neutral surfaces
- crisp borders
- blue-accent / neutral-dark hierarchy
- rounded, controlled, precise

### 4.2. Typography

Primary font:

- `Geist`

Secondary font:

- `Geist Mono` hoặc monospace fallback cho label kỹ thuật

Typography rules:

- Body mặc định: `16px`
- Body secondary: `14px`
- Section label / eyebrow: `12px`, uppercase, medium
- Page title: `40px -> 56px` tùy màn
- Card title: `20px -> 24px`
- Nav label: `15px -> 16px`

Tone:

- display text đậm nhưng không quá black-heavy
- body text dễ đọc, line-height rộng
- tuyệt đối không để block text dài mà thiếu rhythm

### 4.3. Color system

Core palette:

- `#141414` cho darkest neutral
- `#ffffff` cho nền chính
- `#f7f7f5` hoặc `#f8f8f7` cho soft surface
- `#ecebe7` cho border mềm
- `#2f6df6` hoặc gần tương tự cho accent primary
- `#dfeafe` cho primary tint
- `#e9f8ef` cho success tint
- `#fff4dd` cho warning tint
- `#fbe8e8` cho error tint

Nguyên tắc dùng màu:

- chỉ có 1 accent chính
- success/warning/error chỉ dùng cho trạng thái
- không trộn xanh mint cũ với xanh SaaS mới

### 4.4. Radius system

Theo tinh thần ảnh mẫu:

- `8px` cho input nhỏ, chip nhỏ
- `12px` cho badge/container nhỏ
- `16px` cho button, row, side panel items
- `20px` cho card thường
- `24px` cho hero panel
- `32px` cho featured sections
- `40px` chỉ dùng cho bề mặt rất lớn hoặc hero shell

### 4.5. Icon system

Thư viện icon:

- `Lucide React`

Quy tắc:

- icon content: `20px`
- stroke: `1.5` hoặc `1.75`
- icon bound: `32px`
- mọi item nav có icon
- mọi section lớn có icon hoặc visual marker
- không dùng icon màu ngẫu nhiên

## 5. Layout framework

## 5.1. Grid và spacing

Hệ lưới:

- 4px base spacing system
- content grid `12 cột`
- dashboard panels theo `12-column layout`
- card nội bộ theo `8-column` hoặc `subgrid` tùy màn

Spacing scale chuẩn:

- `4`
- `8`
- `12`
- `16`
- `20`
- `24`
- `32`
- `40`
- `48`
- `64`

Không dùng:

- 7
- 10
- 14
- 18
- 22
- 26
- 30

### 5.2. App shell

Shell chuẩn cho ứng dụng:

- Sidebar trái cố định
- Top toolbar/search bar phía trên content
- Main content ở phải
- Content panels bên trong chia theo grid

Kích thước đề xuất:

- Sidebar desktop: `272px`
- Sidebar collapsed rail: `84px`
- Top bar height: `72px`
- Page content padding desktop: `32px`
- Panel gap: `24px`

### 5.3. Responsive

Breakpoint đề xuất:

- `sm`: 640
- `md`: 768
- `lg`: 1024
- `xl`: 1280
- `2xl`: 1536

Hành vi:

- mobile: sidebar thành drawer
- tablet: sidebar thu gọn
- desktop: sidebar full
- grid cards giảm cột nhưng không phá row alignment

## 6. Information architecture mới

## 6.1. Triết lý IA

Không tổ chức UI theo kiểu “mỗi route là một trang rời rạc”.

Tổ chức lại theo 2 nhóm:

- `Shopper flow`
- `Operator flow`

Và cùng nằm trong một app shell chung để demo nhất quán.

## 6.2. Route map đề xuất

### Public / Shopper

- `/`
  - landing / overview
- `/products`
  - product explorer
- `/products/:slug`
  - product detail
- `/cart`
  - cart
- `/orders/:id`
  - order success / order detail

### Internal / Operator

- `/dashboard`
  - operations dashboard
- `/gateway`
  - gateway health & route visibility

### Future AI

- `/assistant`
  - AI recommendation / guided shopping
- `/insights`
  - AI/operator insight page

## 6.3. Sidebar structure

Sidebar dọc thống nhất:

- Logo / brand block
- Search shortcut / quick action
- Main navigation
- Secondary navigation
- Utility/footer area

Nhóm menu đề xuất:

### Main

- `Overview`
- `Products`
- `Categories`
- `Cart`
- `Orders`

### Operations

- `Dashboard`
- `Gateway`
- `Services`

### Future

- `AI Assistant`
- `AI Insights`

### Utility

- `Settings`
- `Theme`
- `Profile`

Mỗi item phải có:

- icon
- label
- active state
- hover state
- selected background

## 7. Page-by-page UI spec

## 7.1. Overview / Landing

Mục tiêu:

- giới thiệu hệ NovaMarket
- cho thấy flow chính
- dẫn nhanh vào browse products

Cấu trúc:

- top hero area
- highlight stats
- featured categories
- quick preview of product grid
- quick preview of order/service state

Visual:

- hero card lớn, sáng
- CTA chính rõ ràng
- card phụ cân nhau

## 7.2. Product Explorer

Mục tiêu:

- là màn quan trọng nhất của shopper flow
- dùng sidebar + top search bar
- hiển thị catalog theo grid rất chuẩn

Cấu trúc:

- page heading
- toolbar:
  - search
  - sort
  - filter chips
- left filter rail hoặc filter panel nếu cần
- product grid

Product card rules:

- media ratio cố định
- title 2-line clamp
- price row cố định
- metadata row cố định
- action row cố định
- button alignment tuyệt đối

Không được phép:

- card này cao thấp lệch logic
- button card lệch baseline
- text description card dài ngắn làm vỡ grid

## 7.3. Product Detail

Mục tiêu:

- rõ
- sạch
- có hierarchy mạnh
- dễ chuyển sang cart

Cấu trúc:

- gallery / hero media trái
- summary phải
- specs
- service/policy notes
- related products

## 7.4. Cart

Mục tiêu:

- nhanh
- ít friction
- nhìn như checkout panel của product thật

Cấu trúc:

- line items list
- right summary panel
- quick checkout button
- shipping/payment chỉ là placeholder nhẹ, không làm thành form nặng

Nguyên tắc:

- không bắt user nhập đống field demo
- cart item row phải thẳng hàng:
  - ảnh
  - tên
  - số lượng
  - giá
  - action

## 7.5. Order Success

Mục tiêu:

- xác nhận giao dịch rõ ràng
- nhìn sáng và “đã hoàn tất”
- cho thấy payment/shipping state

Cấu trúc:

- success summary
- order items
- payment status
- shipping status
- next actions

## 7.6. Dashboard

Đây là màn phải bám rất sát ảnh 1.

Mục tiêu:

- analytics-like
- sidebar rõ
- top search/toolbar rõ
- cards thẳng hàng
- table/list rõ ràng

Modules:

- KPI cards
- recent orders
- payment summary
- shipping summary
- system health snapshot

## 7.7. Gateway

Mục tiêu:

- operator-facing
- clean, technical, nhưng vẫn cùng visual system

Modules:

- service cards
- route registry
- health status
- latency / state badges

Không được:

- trông như một trang admin rời khỏi hệ

## 8. Component inventory

## 8.1. Layout components

- `AppShell`
- `Sidebar`
- `SidebarSection`
- `SidebarItem`
- `TopBar`
- `PageHeader`
- `SectionBlock`
- `GridPanel`

## 8.2. Display components

- `StatCard`
- `ProductCard`
- `ServiceCard`
- `OrderRow`
- `StatusBadge`
- `MetricChip`
- `InfoTile`
- `SectionEyebrow`

## 8.3. Form & interaction

- `SearchInput`
- `SegmentedControl`
- `FilterChip`
- `PrimaryButton`
- `SecondaryButton`
- `IconButton`
- `Drawer`
- `Dialog`
- `Toast`

## 8.4. Feedback states

- `EmptyState`
- `LoadingSkeleton`
- `InlineError`
- `SuccessBanner`

## 9. Alignment rules bắt buộc

Đây là phần không được phá.

### 9.1. Text alignment

- Page title luôn cùng baseline với action area.
- Section title luôn cùng khoảng cách với eyebrow.
- Card title, description, metadata phải theo cùng vertical rhythm.

### 9.2. Button alignment

- Tất cả CTA chính cùng chiều cao.
- CTA trong card luôn nằm đúng hàng cuối card.
- Secondary action không được cao thấp khác primary.

### 9.3. Grid alignment

- Các card cùng group phải có row structure giống nhau.
- Bất kỳ grid nào trên desktop phải có logic column rõ trước khi code.
- Không để auto content height phá visual row.

### 9.4. Icon alignment

- Icon nav, icon KPI, icon chip dùng cùng khung 32px.
- Không để icon chạm sát text hoặc lệch optical center.

## 10. Motion và interaction

Motion phải tiết chế.

Cho phép:

- fade nhẹ
- slide nhẹ
- hover elevation rất nhỏ
- active state rõ

Không cho phép:

- animation loè loẹt
- spring quá mạnh
- gradient động không cần thiết

## 11. Ảnh và media

### 11.1. Hướng dùng ảnh

Sản phẩm phải có ảnh thật hoặc ảnh mockup sạch.

Quy tắc:

- cùng aspect ratio trong grid
- nền ảnh sạch
- không lẫn phong cách ảnh quá chênh nhau
- ưu tiên ảnh lifestyle sáng, neutral

### 11.2. Chỗ dùng media

- product grid
- product detail
- order success
- overview highlights

## 12. Đề xuất implementation architecture

## 12.1. Frontend app structure

```text
services/web_frontend/
  src/
    app/
      router/
      providers/
      layouts/
    components/
      ui/
      shell/
      commerce/
      dashboard/
      gateway/
    features/
      overview/
      products/
      cart/
      orders/
      dashboard/
      gateway/
      assistant/
    lib/
      api/
      utils/
      constants/
      schemas/
    styles/
```

## 12.2. API access pattern

Frontend React chỉ gọi qua gateway:

- `/api/products/*`
- `/api/cart/*`
- `/api/orders/*`
- `/api/payments/*`
- `/api/shipping/*`
- `/api/ai/*`
- `/gateway/health`

Không gọi trực tiếp từng service trong browser.

## 12.3. State management

Phân tách:

- `TanStack Query` cho server state
- local component state cho UI
- chỉ dùng `Zustand` nếu thật sự cần shared UI state như sidebar collapse hoặc command palette

## 13. Kế hoạch build UI

## Phase A. Foundation

- scaffold React + TypeScript + Vite
- setup Tailwind
- setup font Geist
- setup tokens
- setup router
- setup query client
- setup icon system

Đầu ra:

- app chạy được
- sidebar shell dựng xong
- top bar dựng xong

## Phase B. Design system

- button system
- badge system
- card system
- form primitives
- skeleton/loading/empty states

Đầu ra:

- Storybook hoặc page sandbox nội bộ để test component

## Phase C. Shopper flow

- overview
- product explorer
- product detail
- cart
- order success

Đầu ra:

- flow `browse -> cart -> checkout -> success` hoàn chỉnh về UI

## Phase D. Operator flow

- dashboard
- gateway

Đầu ra:

- operator shell đồng nhất với shopper shell

## Phase E. Visual polish

- icon pass
- spacing pass
- alignment pass
- responsive pass
- keyboard/accessibility pass

## 14. Definition of Done cho UI

UI chỉ được xem là “xong” khi đạt đủ:

- không còn template/render thừa từ lớp cũ
- sidebar dọc hoạt động rõ ràng
- mọi page cùng một design system
- mọi button cùng hierarchy và kích thước hợp lý
- icon đầy đủ, cùng family
- grid không lệch
- text không lệch baseline
- mobile/tablet/desktop đều ổn
- flow commerce chính chạy được qua gateway

## 15. Kết luận

Khuyến nghị chính thức:

- **dừng hẳn hướng Django templates + CSS/HTML thuần cho UI chính**
- **chuyển sang React + Tailwind + component system nghiêm túc**
- **dùng app shell/sidebar dọc làm cấu trúc trung tâm**
- **build lại UI như một frontend product thực thụ, không vá tiếp lớp cũ**

`UI_Plan.md` này là tài liệu gốc để bắt đầu phase build frontend mới ngay sau khi chốt:

- cấu trúc route
- component inventory
- token system
- service integration path
