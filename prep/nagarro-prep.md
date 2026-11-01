# Interview Preparation Guide — Nagarro
**Role**: Senior Staff Engineer, Mobile Android
**SmartRecruiters Job ID**: `743999905509553` | **Location**: Remote (UAE / India)

---

## 1. Role & Engineering Context
- **Company**: **Nagarro** is a global digital product engineering leader (`18,000+` engineers across 36 countries) building mission-critical mobile platforms for aviation (Lufthansa, Emirates partners), banking, automotive, and retail clients.
- **What Nagarro Evaluates for Senior Staff Engineer**:
  1. **Enterprise Architecture & Multi-App White-Labeling**: Designing a single multi-module Android / KMP codebase that powers multiple regional brands/clients via Gradle product flavors & dependency injection.
  2. **Deep Kotlin, Jetpack Compose & Coroutines Mastery**.
  3. **Technical Consulting & Client Architecture Governance**: Translating ambiguous business problems into scalable mobile blueprints and leading 8–15 person engineering squads.

---

## 2. Mobile System Design Scenario
### **Prompt**: *"Architect a Multi-Tenant White-Label Enterprise Mobile Platform with Offline Sync & Conflict Resolution."*
- **Key Architectural Pillars to Present**:
  1. **Clean Architecture + Multi-Module Gradle Setup**:
     - `:app` (thin shell + DI graph), `:core:designsystem` (Compose theme tokens per tenant), `:core:network`, `:core:sync`, and independent `:feature:*` modules.
  2. **Bi-Directional Offline Sync Engine**:
     - Local Room DB stores entities with `sync_status (SYNCED, DIRTY_CREATE, DIRTY_UPDATE, CONFLICT)` + vector clock / `updated_at` version tag.
     - `WorkManager` with `NetworkType.CONNECTED` flushes dirty records in batches and resolves conflicts deterministically.
  3. **CI/CD & Quality Gates**:
     - Automated Detekt/Ktlint, Jacoco unit test coverage (`>80%` on domain/ViewModels), Play Store / Firebase App Distribution matrix builds.

---

## 3. High-Probability Technical Questions
1. **Dagger/Hilt Scopes**: *"Explain `@Singleton`, `@ActivityRetainedScoped`, and `@ViewModelScoped` in multi-module apps."*
2. **Compose State Hoisting & Unidirectional Data Flow (UDF)**: *"How do you design stateless, reusable Design System composables across enterprise teams?"*
3. **Legacy Migration Strategy**: *"How do you incrementally migrate a 5-year-old Java/XML/RxJava app to Kotlin + Jetpack Compose + Coroutines without freezing feature delivery?"*
   - **Your Answer**: Strangler-fig pattern using `ComposeView` inside existing Fragments for new screens, `rx2coroutines` (`Flow.asObservable()` / `Observable.asFlow()`) bridges at repository boundaries, and migrating bottom-up from data/domain layers.

---

## 4. Compensation Alignment
- **Submitted Figures**: `12 years` experience | Notice Period: `30 days` | Quoted Expected Compensation: **`AED 30,000 – 32,000 / month` (or `₹38.0 – 42.0 LPA` INR)**.
