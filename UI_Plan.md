# UI Plan: NovaMarket Visual System

## 1. Single visual direction

The project will now follow one strict UI direction only:

- bright interface
- clean SaaS dashboard feel
- left vertical sidebar navigation
- calm blue accent
- soft gray surfaces
- strong spacing discipline
- low-noise typography
- thin borders instead of heavy shadows

The reference style is the compact analytics dashboard aesthetic from the supplied images, not a generic e-commerce landing page.

## 2. Core layout language

The entire product should feel like one connected application shell:

- fixed vertical sidebar on desktop
- slim top bar inside the main content area
- content sections placed inside large rounded panels
- wide internal padding and consistent whitespace
- card grids for metrics, products, and admin summaries

Desktop structure:

- left sidebar: `240px` to `264px`
- main canvas: fluid
- content max width: `1200px` inside the canvas

Mobile structure:

- collapsible sidebar
- stacked cards
- one-column flow for cart, checkout, and detail pages

## 3. Typography

Primary font:

- `Geist`

Fallback:

- `Inter`, `ui-sans-serif`, `system-ui`, `sans-serif`

Sizing:

- body default: `16px`
- compact body: `14px`
- page title: `40px` to `48px`
- section title: `24px` to `32px`
- card title: `18px` to `20px`
- eyebrow / metadata: `12px`

Rules:

- short headings
- low paragraph density
- avoid decorative text
- every sentence on screen must earn its place

## 4. Color system

Primary palette:

- `Background`: `#F6F7FB`
- `Surface`: `#FFFFFF`
- `Surface Soft`: `#F3F5F8`
- `Surface Accent`: `#EEF4FF`
- `Border`: `#E5EAF1`
- `Border Strong`: `#D8E0EA`
- `Text Primary`: `#141414`
- `Text Secondary`: `#5F6878`
- `Text Tertiary`: `#8A93A3`
- `Primary Blue`: `#5B7CFA`
- `Primary Blue Hover`: `#4D6EEF`
- `Primary Blue Soft`: `#EAF0FF`
- `Success`: `#61B38C`
- `Warning`: `#E9B55A`
- `Danger`: `#D96B6B`

Rules:

- most of the UI stays neutral
- blue is used for active state, primary CTA, selected chips, and key metrics
- avoid saturated gradients except for small accents

## 5. Spacing and rhythm

Spacing must follow a strict 4px rhythm:

- `4`, `8`, `12`, `16`, `20`, `24`, `32`, `40`, `48`, `64`

Rules:

- do not stack dense content blocks without separators
- cards need breathing room
- grid gaps must remain visually even
- avoid text glued to buttons, panels, or borders

## 6. Radius, border, depth

Radius:

- input: `12px`
- button: `14px` to `16px`
- small card: `18px`
- panel card: `24px`
- application shell blocks: `28px` to `32px`

Depth:

- prefer border-first styling
- shadows must be soft and wide
- no heavy black drop shadows

## 7. Sidebar specification

Sidebar style follows the first reference:

- vertical navigation
- logo at top
- grouped navigation links
- soft selected state
- compact icons or icon placeholders
- muted secondary area under the main nav

Sidebar sections:

1. brand
2. primary navigation
3. utility links
4. account / auth action

Primary nav items:

- Home
- Products
- Cart
- Dashboard
- Gateway

## 8. Top bar specification

Each main page should have a slim top bar with:

- page context
- optional search field
- quick status or shortcut pill
- auth action or primary CTA

The top bar should feel like part of the app shell, not a marketing navbar.

## 9. Screen-by-screen implementation

### Home

Purpose:

- present the storefront cleanly
- show the project quality immediately
- avoid wordy course-project framing

Structure:

- page intro row
- hero panel with concise title and CTA
- compact metric cards
- category grid
- featured products grid

### Products

Purpose:

- fast browsing
- clean filters
- low-friction product scanning

Structure:

- page intro row
- search + filter chips
- product grid
- empty state when no products match

### Product detail

Purpose:

- premium product presentation
- clear purchase action

Structure:

- two-column detail panel
- product visual card
- product information column
- specification cards
- strong add-to-cart CTA
- related products

### Cart and checkout

Purpose:

- follow the second reference style
- clean summary-first layout
- strong visual grouping

Structure:

- page intro row
- left column: cart items in neat stacked panels
- right column: summary card + checkout form card
- generous spacing
- minimal supporting copy

### Admin dashboard

Purpose:

- also follow the second reference style
- look like an analytics workspace, not a default Django admin mock page

Structure:

- page intro row
- metric cards
- recent orders panel
- optional system/service health panel
- strong table spacing and clean headers

### Login

Purpose:

- minimal
- polished
- consistent with app shell

Structure:

- centered auth card
- concise explanation
- clean form fields

## 10. Copy rules

The current product has too much explanatory text. The rebuilt UI should follow these rules:

- one strong title per screen
- one short supporting paragraph at most
- no long educational text inside the main commerce flow
- no AI references for now
- no duplicated labels

## 11. Interaction rules

- add-to-cart must work through the gateway
- login must work through the gateway
- checkout must work through the gateway
- sidebar active state must clearly reflect the current page
- mobile nav must collapse cleanly

## 12. Final target

After the rebuild, the UI should feel like:

- one coherent application shell
- cleaner and calmer than the current MVP
- suitable for final demo screenshots
- visually aligned with the supplied references
