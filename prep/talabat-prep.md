# Talabat (Delivery Hero) — Interview Preparation Guide

**Target Role**: Manager Engineering - Mobile / Lead Mobile Architect (iOS & Android)  
**Location**: Dubai, UAE (City Walk / Regional Tech Hub)  
**Target Compensation**: AED 32,000–35,000 / month (~₹88 LPA tax-free equivalent, + immediate relocation)  

---

## 1. Interview Loop Structure & Evaluation Rubric
1. **Screening Call (30–45 mins)**: Engineering Recruiter / Talent Lead — Career overview, mobile engineering leadership scale, reason for Dubai relocation, and compensation expectations.
2. **Technical Architecture & System Design (60 mins)**: Mobile Principal / Director of Engineering — Design a high-concurrency food delivery / quick-commerce mobile app (live rider tracking, real-time checkout state machine, battery-efficient background location, offline cache synchronization).
3. **Engineering Management & Squad Leadership (60 mins)**: Senior Engineering Manager / Head of Tech — eXtreme Programming (XP), TDD/pairing culture, handling technical debt vs. feature velocity, cross-platform alignment (iOS & Android), and mentoring junior/senior engineers.
4. **Product Partnership & Culture Fit (45 mins)**: Product Director & People Lead — Cross-functional collaboration with PMs and Design, balancing user impact with engineering feasibility, conflict resolution, and life in Dubai.

---

## 2. Mobile System Design Blueprint: Real-Time Order & Live Tracking Pipeline
- **Problem**: Support millions of concurrent customers tracking order preparation, dispatch, and live rider GPS location updates across the GCC without draining device battery or dropping state.
- **Architectural Solution**:
  - **Transport Layer**: MQTT / WebSocket bidirectional channel with exponential backoff heartbeat and adaptive polling fallback (HTTP/2 SSE).
  - **Client Concurrency**: Kotlin Coroutines `SharedFlow` with `BufferOverflow.DROP_OLDEST` and conflation to avoid UI thread saturation during burst location telemetry updates.
  - **Map & Animation Engine**: Decoupled Mapbox/Google Maps rendering layer using custom interpolation curves (`LinearInterpolator` with bearing smoothing) to prevent rider marker jumping.
  - **Offline & Resiliency**: Local-first Room DB with transactional order state machines (`PLACED` &rarr; `CONFIRMED` &rarr; `PREPARING` &rarr; `ON_THE_WAY` &rarr; `DELIVERED`). Every transition is backed by a deterministic idempotency key (`UUIDv4`).

---

## 3. Deep-Dive Technical Q&A
- **Q1: How do you enforce consistent mobile engineering standards across separate iOS and Android teams?**
  - *Model Answer*: Establish a unified **Mobile Chapter RFC process** where architectural changes (network layer, authentication, caching contracts, analytics schemas) are reviewed collaboratively. Align design systems through shared Figma design tokens exported via automated scripts to Compose and SwiftUI theme primitives. Enforce contract testing via OpenAPI / Protobuf specs to ensure identical network serialization across platforms.
- **Q2: How do you introduce TDD and XP practices to a team accustomed to shipping without tests?**
  - *Model Answer*: Start with high-ROI areas: view models and business domain use cases, where mock dependencies are trivial. Implement mob/pair programming sessions on critical user flows (e.g., checkout/payment). Set automated CI test coverage gates on new PRs (>80% on domain modules) rather than enforcing retroactive coverage on legacy code, demonstrating how TDD accelerates refactoring and cuts crash rates.
- **Q3: How do you handle cold start latency on high-scale Android e-commerce apps?**
  - *Model Answer*: Profile startup with Android Studio Macrobenchmark and Perfetto. Defer non-critical SDK initializations (analytics, crashlytics, push tokens) using Android App Startup with background coroutine dispatchers. Generate and ship Baseline Profiles to pre-compile critical execution paths (Splash &rarr; Home &rarr; Search &rarr; Menu) ahead-of-time with R8.

---

## 4. STAR Stories Mapped to Past Career
- **Situation (Guardian)**: Multi-squad mobile development caused feature conflicts, build delays, and inconsistent UI patterns.
- **Task**: Restructure mobile architecture to support independent squad deployments with zero regression.
- **Action**: Spearheaded Clean Architecture modularization, isolating `:feature`, `:core:network`, and `:core:designsystem` modules with strict API boundary visibility. Instituted automated GitHub Actions CI checks and weekly architectural triage.
- **Result**: Cut clean build times by 35%, eliminated merge bottlenecks, and maintained 99.7%+ crash-free session rates across all releases.

---

## 5. Compensation & Relocation Script
> *"Based on my 11+ years of engineering experience, current role as Lead Mobile Engineer / Architect at Guardian, and track record leading high-concurrency mobile systems, I am targeting **AED 32,000–35,000 per month tax-free** for this Engineering Manager / Mobile Architect position at Talabat. I am fully prepared for immediate relocation to Dubai and excited to lead your mobile squads across the MENA region."*
