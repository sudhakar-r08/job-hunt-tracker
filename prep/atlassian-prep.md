# Atlassian — Interview Preparation Guide

**Target Role**: Senior Mobile Android Engineer (Audit Platform & Guard) (Req: 26530)  
**Location**: Bengaluru, Karnataka, India (Team Anywhere / Hybrid)  
**Target Compensation**: ₹42.0 LPA (+50% hike on current 28 LPA baseline, well-positioned within Atlassian Senior Mobile band)  

---

## 1. Interview Loop Structure & Evaluation Rubric
1. **Recruiter Screen (30 mins)**: Career journey, experience at Guardian (Mobile Architect), Ayla Networks (Lead SDE), and Vectone Mobile. Discussion of Atlassian's "Team Anywhere" culture, motivation for joining Atlassian Guard and Audit Platform, notice period (90 days, negotiable), and target compensation (₹42.0 LPA).
2. **Technical Screen / Live Coding & Kotlin Concurrency (60 mins)**: HackerRank / CoderPad live coding. Tests clean Kotlin idiomatic code, concurrency primitives (Coroutines, Flow, StateFlow, Mutex), collections, data transformations, error handling, and unit test coverage.
3. **Mobile System Design & Architecture (60 mins)**: High-level architectural design for an enterprise mobile security & audit telemetry platform (e.g., Designing the Atlassian Guard Mobile Audit Log Viewer & Incident Response Dashboard). Evaluates multi-module modularization, offline caching, push notification / real-time alerting via WebSockets/SSE, token security (Keystore, OAuth 2.0/SAML), and battery-conscious background synchronization.
4. **Deep-Dive Android Internals, Security & DevEx (60 mins)**: Technical deep-dive into Android security sandbox, hardware Keystore, BiometricPrompt, mTLS certificate pinning, memory leak prevention, Jetpack Compose recomposition optimization, Baseline Profiles, and CI/CD pipelines.
5. **Atlassian Values & Behavioral Round (60 mins)**: Focuses on Atlassian's 5 core values:
   - *Open company, no bullshit*
   - *Build with heart and balance*
   - *Don’t #@!% the customer*
   - *Play, as a team*
   - *Be the change you seek*

---

## 2. Mobile System Design Blueprint: Atlassian Guard Mobile Audit & Threat Monitoring System
- **Problem Statement**: Design an enterprise Android mobile application for Atlassian Guard and the Audit Platform. Enterprise administrators must securely receive real-time security alerts (e.g., unauthorized IP access, mass export of Jira issues, permission elevation), inspect audit trails with complex multi-criteria filtering, take immediate remediation actions (revoke session, suspend user), and browse logs offline without exposing sensitive enterprise customer data to unauthorized apps or memory dumps.
- **Architectural Solution**:
  - **Security & Identity Foundation (`:core:security`)**:
    - **Encrypted Token Management**: Session tokens (OAuth 2.0 JWTs, refresh tokens) stored using Android Keystore-backed AES-256-GCM encryption with `EncryptedSharedPreferences` / Jetpack DataStore.
    - **Biometric & Step-Up Authentication**: Enforces `BiometricPrompt` with `CryptoObject` before authorizing destructive remediation actions (e.g. revoking enterprise org tokens).
    - **Network Security**: Mutual TLS (mTLS) with public key certificate pinning via Network Security Configuration and OkHttp CertificatePinner.
    - **Tamper & Jailbreak Detection**: Integrity verification using Play Integrity API; prevents app execution on compromised or rooted devices.
  - **Real-Time Alerting & Streaming Pipeline (`:core:network`)**:
    - **Bidirectional Event Stream**: Persistent WebSocket / Server-Sent Events (SSE) connection multiplexed with HTTP/2 keep-alives for sub-second security incident notifications.
    - **FCM High-Priority Push Fallback**: High-priority push alerts trigger background payload processing and urgent heads-up notifications with direct deep-linking to the affected incident.
  - **Offline-First Audit Trail Engine (`:core:database`)**:
    - **Encrypted Local Database**: SQLCipher-backed Room database storing encrypted audit event schemas.
    - **Paging 3 Integration**: Efficient virtualized loading of thousands of audit records with bidirectional prefetching and smooth Compose scrolling.
    - **Dynamic Filtering Engine**: Multi-criteria indexing (Timestamp, Actor, Target Resource, IP, Severity) with full-text search (FTS4) inside SQLite.
  - **Declarative Incident Management UI (`:feature:audit-viewer`)**:
    - **Jetpack Compose**: High-performance UI using Atlassian Design System tokens.
    - **State Management**: Clean MVI / Unidirectional Data Flow using `StateFlow` and immutable UI states (`AuditState.Loading`, `AuditState.Success`, `AuditState.Error`).
    - **Deterministic Frame Rates**: Strict `@Immutable` data classes, derived states with `remember { derivedStateOf { ... } }`, preventing unnecessary recompositions during live incident streaming.

---

## 3. Deep-Dive Technical Q&A

- **Q1: How do you secure sensitive audit data and authentication tokens on an Android device to guarantee zero data leakage?**
  - *Model Answer*:
    1. **Hardware-Backed Keystore**: We generate an asymmetric key pair or AES-256 key inside the Android KeyStore provider with `PURPOSE_ENCRYPT | PURPOSE_DECRYPT`. On modern devices, keys are protected by the hardware Secure Element (SE) or StrongBox Keymaster.
    2. **Encrypted Persistence**: Tokens and cached audit payloads are encrypted using Jetpack Security (`EncryptedSharedPreferences` / SQLCipher) so raw bytes never sit plaintext in app private storage.
    3. **Memory Hygiene**: Sensitive tokens are wiped from memory (zeroed out character arrays) once authentication headers are constructed, avoiding lingering references in heap dumps.
    4. **Screenshot & Screen Recording Prevention**: `WindowManager.LayoutParams.FLAG_SECURE` is applied across all security and audit screens, blocking unauthorized OS screenshots, recent apps switcher thumbnails, and remote screencasts.
    5. **Network Integrity**: TLS 1.3 with Certificate Pinning prevents Man-in-the-Middle (MitM) attacks even on compromised enterprise Wi-Fi networks.

- **Q2: In Jetpack Compose, how do you prevent performance degradation and UI jank when displaying high-frequency live audit event feeds?**
  - *Model Answer*:
    1. **Unidirectional Data Flow with StateFlow**: The ViewModel ingests high-frequency WebSocket events into an internal buffer and emits throttled/batched updates to the UI via `StateFlow` (e.g. throttling updates to 60fps intervals using `flow.sample(16.ms)`).
    2. **Stability & Immutability**: Annotate all event models with `@Immutable` or ensure data classes contain only primitive or immutable properties. This allows Compose to skip recomposing unmodified list items.
    3. **LazyColumn with Stable Keys**: Pass unique, stable identifiers to the `key` parameter in `LazyColumn` (`items(items = auditLogs, key = { it.eventId })`). This ensures items are moved or reordered rather than fully recomposed.
    4. **Deferred State Reads & Sub-Composition**: Pass lambda reads (e.g. `() -> Float`) for animations and dynamic offsets, deferring state reads to the layout or draw phase rather than triggering full recomposition.

- **Q3: How do you design an Android multi-module architecture that accelerates build times and maintains strict boundary isolation?**
  - *Model Answer*:
    1. **Module Separation by Layer & Feature**: Structure the project into `:app`, `:core:*` (e.g., `:core:network`, `:core:database`, `:core:security`, `:core:designsystem`), and `:feature:*` (e.g., `:feature:audit-logs`, `:feature:alerts`, `:feature:settings`).
    2. **API vs Implementation Dependencies**: Use `api` dependencies sparingly and prefer `implementation` to prevent leaky transitive dependencies and allow Gradle to isolate compilation units.
    3. **Inversion of Control & Interface Segregation**: Feature modules never depend directly on other feature modules. Navigation and shared services communicate via interfaces defined in `:core:navigation` or through dependency injection (Hilt/Dagger).
    4. **Build Optimization**: Utilize Gradle configuration cache, build cache, and parallel execution. Modules that have not changed are instantly retrieved from cache, cutting incremental build times by up to 60%.

- **Q4: How does your background at Guardian, Ayla Networks, and Vectone Mobile prepare you for Atlassian Guard?**
  - *Model Answer*: At Guardian, as Lead Mobile Engineer / Architect, I enforce enterprise compliance, hardware Keystore security, and high performance across distributed systems, sustaining 99.85%+ crash-free rates. At Ayla Networks, I led mobile development for enterprise IoT platforms, architecting low-latency WebSocket communication layers and reliable offline caching under strict security standards. At Vectone Mobile, I engineered real-time communication systems and reactive data pipelines. This combination of deep security rigor, real-time networking, enterprise mobile architecture, and collaborative leadership maps directly to Atlassian Guard’s vision of empowering administrators with trusted, high-performance mobile tools.

---

## 4. STAR Stories Mapped to Past Career

### Story 1: Enterprise Cryptographic Keystore & Compliance Hardening (Guardian)
- **Situation**: Guardian required bulletproof client-side security architecture to meet enterprise compliance standards and protect sensitive authorization tokens.
- **Task**: Overhaul the mobile security model and implement hardware-backed encryption with zero vulnerability.
- **Action**: Architected a cryptographic token storage layer utilizing Android Keystore and AES-256-GCM; implemented mutual TLS certificate pinning with automatic rotation fallbacks; enabled `FLAG_SECURE` to prevent screen scraping; and integrated automated static security scans into CI/CD.
- **Result**: Passed third-party enterprise security audits with zero high-severity vulnerabilities and established the security blueprint for all Guardian mobile applications.

### Story 2: Real-Time Event Streaming & Low-Latency Telemetry (Ayla Networks)
- **Situation**: Ayla's enterprise IoT mobile platform needed to process thousands of live device state changes and security events with sub-second latency.
- **Task**: Replace legacy polling with an ultra-responsive real-time event pipeline.
- **Action**: Engineered a persistent WebSocket communication layer with intelligent reconnect backoff and heartbeat health checks; coupled it with reactive Kotlin Flow pipelines and Room DB caching for instant offline availability.
- **Result**: Reduced event latency by 75%, decreased server load by 40%, and eliminated missed alerts across thousands of connected appliances.

---

## 5. Compensation Negotiation Script
- **Recruiter**: "Sudhakar, what are your compensation expectations for this Senior Mobile Android Engineer role in Bengaluru?"
- **Candidate (Sudhakar)**: "My current fixed CTC at Guardian is ₹28 LPA. For this Senior Mobile Android Engineer position at Atlassian within the Audit Platform & Guard team, my target compensation is **₹42.0 LPA fixed CTC** (+50% hike). This is well-aligned with Atlassian's Senior Engineering compensation band in Bengaluru and reflects the extensive mobile architecture, enterprise security, real-time networking, and engineering leadership I will bring from Day 1 to accelerate Atlassian Guard's mobile roadmap."
