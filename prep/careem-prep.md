# Interview Preparation Guide — Careem
**Role**: Software Engineer II / Senior Engineer — NextGen Engineering (Super App Platform)
**Greenhouse ID**: `7004825002` | **Location**: Dubai, UAE / MENA

---

## 1. Role & Product Context
- **Product**: **Careem Everything App** — the Middle East's flagship Super App (Ride-hailing, Careem Pay, Careem Food, Quik Grocery, Hala Taxi, and third-party Mini-Apps) serving 50M+ users across 70+ cities.
- **Key Focus Areas**: High-throughput distributed systems & mobile-backend API contracts, low-latency geo-location/dispatch pipelines, modular Super-App architecture, and operational excellence.

---

## 2. Super-App System Design Scenario
### **Prompt**: *"Design the Careem Super-App Home Screen & Real-Time Captain (Driver) Location Tracking Pipeline."*
- **Key Architectural Pillars to Present**:
  1. **Server-Driven UI (SDUI) for the Super-App Home Screen**:
     - With 15+ verticals (Rides, Food, Pay, Groceries), hardcoding layouts requires Play Store releases for every campaign. Design a **Server-Driven UI schema** (JSON/Protobuf widget tree rendered natively via Jetpack Compose / RecyclerView view-types) with local caching and schema-version fallback.
  2. **Real-Time Geo-Location & Map Interpolation**:
     - Captains stream GPS coordinates every 3–5 seconds over **MQTT / gRPC / WebSockets** indexed via **Uber H3 hexagonal spatial indexes**.
     - On the client, use a **Kalman filter + dead-reckoning linear interpolation** along road polylines so the vehicle marker glides smoothly at 60 FPS even when packets arrive jittery.
  3. **Resilience & Circuit Breaking**:
     - Isolate vertical failures: if the Food Recommendation microservice degrades, the Super-App home screen gracefully renders Rides & Careem Pay without blocking startup.

---

## 3. High-Probability Technical & Behavioral Questions
1. **Careem Ownership Values ("Be of Service", "Shoot for the Moon", "Own It")**:
   - Use your **Vectone Mobile ('Worktual')** and **Ayla Networks** leadership stories where you owned end-to-end product stability, reduced crash rates to `<0.4%`, and mentored cross-functional engineers from design to production rollout.
2. **API Design & Mobile Network Efficiency**:
   - Explain payload compression, pagination, ETag caching, and GraphQL/BFF (Backend-for-Frontend) aggregation to minimize mobile radio wakeups and tail latency (`p99`).

---

## 4. Compensation Alignment
- **Target Compensation**: **`AED 30,000 – 35,000 / month`** (or equivalent band for Remote/Dubai relocation).
