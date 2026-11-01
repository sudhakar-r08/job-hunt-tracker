# Interview Preparation Guide — Deloitte (ConvergeSPORTS USI)
**Role**: Mobile App Dev - Android Engineer - Software Engineer III (Senior Consultant)
**Requisition ID**: `#370968` | **Hiring Manager / Reports To**: **Li-Shen Lee** | **Location**: Chennai, Tamil Nadu

---

## 1. Role & Team Context (What Li-Shen Lee's Team Cares About)
- **Product**: **ConvergeSPORTS Mobile App** — a fan-facing consumer digital product for sports leagues, teams, venues, and media organizations combining content, identity, fan engagement, personalization, push notifications, and commercial ticketing/merchandise experiences.
- **Your Accountability**: You are the hands-on Android owner closest to the codebase—accountable for **frame-rate smoothness, memory/battery efficiency, Kotlin + Jetpack Compose architecture, RESTful API integration, unit/UI test coverage, and Google Play Store staged rollouts**.

---

## 2. Mobile System Design Scenario (Likely Round 2)
### **Prompt**: *"Design the ConvergeSPORTS Live Matchday Fan App for 500,000 concurrent stadium & remote fans."*
- **Key Architectural Pillars to Present**:
  1. **Modular Clean Architecture + MVI/MVVM**:
     - Feature modules: `:feature:live-score`, `:feature:fan-identity`, `:feature:personalized-feed`, `:feature:notifications`, `:core:network`, `:core:database`.
  2. **Single Source of Truth (Offline-First Stadium Mode)**:
     - Stadium Wi-Fi/cellular is congested on matchday. Use **Room SQLite + Kotlin `Flow`** as the single source of truth so digital tickets, fan identity QR codes, and cached feeds render in `<50ms` offline.
  3. **Real-Time Score & Personalization Updates**:
     - Combine **FCM high-priority push** + **WebSockets / Server-Sent Events (SSE)** with exponential backoff and jitter so 500k clients don't thunder-herd the backend when a goal/wicket happens.
  4. **60/120 FPS Frame-Rate Optimization in Jetpack Compose**:
     - Use `@Stable` / `@Immutable` UI state models, `derivedStateOf` for scroll-dependent headers, `Baseline Profiles` for startup/scroll compilation, and lazy keys (`LazyColumn(key = { it.id })`) to eliminate unnecessary recompositions during live ticker updates.

---

## 3. High-Probability Android & Kotlin Technical Questions
1. **Jetpack Compose Performance**: *"Fans judge the product by the frame rate they feel. How do you diagnose and fix jank in a media-heavy feed?"*
   - **Your Answer**: Macrobenchmark + Perfetto system tracing + Layout Inspector recomposition counts. Explain skippability rules (avoiding unstable `List<T>` collections by using `ImmutableList` or `@Immutable` wrappers, deferring state reads with lambda modifiers like `Modifier.offset { ... }`).
2. **Coroutines & Structured Concurrency**: *"How do you handle parallel API calls (e.g., loading fan profile, live match stats, and sponsor promos) where one non-critical call fails?"*
   - **Your Answer**: Use `supervisorScope` with `async` blocks so a failure in `sponsorPromosDeferred.await()` returns a fallback state without cancelling `fanProfileDeferred` or `liveStatsDeferred`, tied to `viewModelScope` using `SharingStarted.WhileSubscribed(5_000)`.
3. **Play Store Release & Production Triage**: *"How do you manage Play Store releases and catch regressions early?"*
   - **Your Answer**: CI/CD pipeline running JUnit + Espresso/Compose UI tests -> Internal Track -> Staged Rollout (`5% -> 20% -> 50% -> 100%`) monitored via **Firebase Crashlytics** & Play Vitals (ANR rate `<0.47%`, crash-free `>99.6%`) with feature flags (Firebase Remote Config) for instant kill-switch rollback.

---

## 4. Tailored STAR Stories (From Your Verified Career)
- **Story 1 (Guardian & Ayla Networks — Performance & Stability at Scale)**:
  - *Situation*: High-frequency telemetry and real-time status updates across diverse Android OEM devices caused battery drain and UI stutter.
  - *Action*: Re-architected the data layer using Kotlin Coroutines `Flow` coalescing/conflation, optimized memory allocations, and introduced strict unit testing + staged Play Store rollouts.
  - *Result*: Achieved **99.6%+ crash-free sessions** and reduced background battery consumption by 30%.
- **Story 2 (Vectone Mobile — 'Worktual' Real-Time Consumer Experience)**:
  - *Situation*: Owned end-to-end Android delivery for the flagship Worktual app requiring seamless real-time notifications, media streaming, and cross-team alignment with iOS and Backend.
  - *Action*: Built shared API contracts, standardized MVVM architecture, and led daily sprint syncs across Design, Product, and QA.

---

## 5. Compensation & Closing Alignment
- **Submitted Figures**: Current CTC `₹28.0 LPA` (`₹26L Fixed + ₹2L Variable`) | Quoted Expected CTC: **`₹37.0 LPA`** (`30 days` notice period, Chennai 1st preference).
