# Outreach — Interview Preparation Guide

**Target Role**: Staff Software Engineer (Mobile, Android)  
**Location**: Hyderabad, Telangana, India (Hybrid)  
**Target Compensation**: ₹41.5 LPA (+48.2% hike on current 28 LPA baseline, aligned with Outreach Staff Engineering band in Hyderabad)  

---

## 1. Interview Loop Structure & Evaluation Rubric
1. **Recruiter Screen (30 mins)**: High-level career walkthrough, past experience leading native Android mobile architectures, hybrid setup in Hyderabad, notice period (90 days, negotiable), and target compensation (₹41.5 LPA).
2. **Technical Screen / Live Coding & Fundamentals (60 mins)**: Hands-on Kotlin coding on CoderPad. Data structures, concurrency, Kotlin Coroutines, Flow, structured concurrency, memory management, and clean unit testing.
3. **Android Architecture & Mobile System Design (60 mins)**: Staff / Principal Mobile Architect — Design a high-scale B2B sales execution and telephony mobile application (e.g. Outreach mobile dialer, call recording, Apollo GraphQL state sync, and real-time task notifications). Evaluates multi-module layering, offline caching, Android Telecom framework integration, and network resilience.
4. **Engineering Craft, Design Systems & Modernization (60 mins)**: Senior Engineering Manager / Staff Mobile Engineer — Jetpack Compose Material 3 design system architecture, modularization patterns, Apollo Kotlin 4 migrations, CI/CD automated release trains on Google Play, and performance profiling (Baseline Profiles, R8, ANR elimination).
5. **Staff Engineering Leadership & Behavioral Alignment (45 mins)**: VP / Director of Engineering — Mentoring senior engineers, driving architectural RFCs across distributed teams, aligning technical initiatives with product revenue goals, and handling production incidents.

---

## 2. Mobile System Design Blueprint: Outreach AI Sales Execution & Telephony Platform
- **Problem Statement**: Design the core client mobile architecture for the Outreach Android application. Sales representatives need to manage sales pipelines on the road: make outbound VoIP/cellular calls via Twilio with automatic call recording, receive real-time SMS/tasks, query GraphQL APIs with optimistic UI updates, interact with "Ask Outreach" AI agents, and work seamlessly offline. The app must ensure sub-16ms UI responsiveness, bulletproof offline task persistence, background call reliability across aggressive Android OEM battery killers, and enterprise-grade security (Microsoft Intune compliance).
- **Architectural Solution**:
  - **Multi-Module Clean Architecture (`:app`, `:core:network`, `:core:database`, `:core:telecom`, `:core:designsystem`, `:feature:dialer`, `:feature:tasks`, `:feature:ai-agent`)**:
    - Decoupled into strict layers: Presentation (Jetpack Compose / MVI), Domain (UseCases, Sales Business Logic), and Data (Repositories, Room DB, Apollo GraphQL Client).
    - Eliminates circular dependencies and cuts Gradle incremental build times by 45%.
  - **Telephony & Real-Time Voice Integration (`:core:telecom`)**:
    - **Android Telecom Framework (`ConnectionService`)**: Integrates Twilio Voice calls directly with the native Android operating system call manager. This provides native in-call UI, Bluetooth headset/car integration, and native call-hold handling.
    - **Foreground Services & Audio Focus**: Manages audio streams with `AudioManager.requestAudioFocus()` to guarantee zero voice dropouts during multi-tasking.
    - **FCM High-Priority Signaling**: Inbound calls are triggered via high-priority FCM data messages that awaken the app and launch a full-screen Intent without battery-saver throttling.
  - **Data Layer & Apollo GraphQL Architecture (`:core:network`)**:
    - Utilizes **Apollo Kotlin 4** with normalized in-memory and SQLite cache.
    - Implements optimistic UI updates for task completions and pipeline stage changes, reconciling server state upon GraphQL mutation completion.
  - **Offline Task Persistence & Sync Engine (`:core:database`)**:
    - Encapsulates local mutations in a transactional queue using **Room DB**.
    - Employs **WorkManager** with exponential backoff and network constraints (`NetworkType.CONNECTED`) to guarantee eventual consistency without draining battery.
  - **Agentic AI Assistant ("Ask Outreach")**:
    - Streams LLM responses chunk-by-chunk over WebSockets/SSE directly into Jetpack Compose `LazyColumn` using `StateFlow`, rendering real-time markdown and action chips at 60fps.

---

## 3. Deep-Dive Technical Q&A

- **Q1: How do you integrate a real-time VoIP dialer (such as Twilio Voice) into Android to ensure incoming and outgoing calls behave like native phone calls?**
  - *Model Answer*:
    1. **`ConnectionService` Integration**: We extend Android's `ConnectionService` (from `android.telecom`) and register a custom `PhoneAccount`. This tells the Android OS that our app can manage cellular/VoIP calls, integrating directly with Android's native call screen, Bluetooth automotive systems, and lock-screen dialers.
    2. **Audio Focus & Routing**: We request `AUDIOFOCUS_GAIN_TRANSIENT_EXCLUSIVE` via `AudioManager.requestAudioFocus()` and register audio device callbacks to gracefully handle Bluetooth SCO headset connects/disconnects and speakerphone toggles.
    3. **Background Awakening**: Inbound call alerts are sent via high-priority FCM data messages (`priority: "high"`). On receiving the payload, we invoke `TelecomManager.addNewIncomingCall()`, which displays a heads-up notification with a full-screen `PendingIntent` without requiring the app to be open in the foreground.
    4. **Microphone Permissions & Foreground Service**: When an active call connects, we bind a `Service` with `foregroundServiceType="microphone|phoneCall"` under Android 14+ rules to prevent OS process termination during backgrounding.

- **Q2: How do you architect an Apollo GraphQL client layer in Android to support optimistic updates and offline caching?**
  - *Model Answer*:
    1. **Normalized Cache (`SqlNormalizedCache`)**: In Apollo Kotlin 4, we configure a normalized cache backed by SQLite. Records are indexed by their global unique identifier (`id` or `typename:id`), ensuring that when a query updates a contact or task record, every other query observing that record updates automatically.
    2. **Optimistic Mutations**: When a sales rep marks a task completed or updates a pipeline stage, we dispatch an optimistic mutation payload into Apollo's cache immediately. The Compose UI updates in 0ms. If the network call fails, Apollo automatically rolls back the cache to the previous snapshot and displays an inline retry banner.
    3. **Coroutines & Flow Integration**: Apollo queries are exposed as Kotlin `Flow` streams (`apolloClient.query(query).toFlow()`), allowing ViewModels to collect UI state reactively without manual event bus notifications.

- **Q3: How do you build and maintain a scalable Material 3 Design System in Jetpack Compose across multiple feature teams?**
  - *Model Answer*:
    1. **Design Tokens in `:core:designsystem`**: Centralize typography, color schemes (supporting dynamic color, light, and dark mode), shapes, and elevations into immutable data objects.
    2. **Custom Component Library**: Wrap Material 3 primitives into domain-specific components (e.g. `OutreachButton`, `SalesPipelineCard`, `ProspectAvatar`) that enforce consistent padding, accessibility labels, and interaction feedback.
    3. **Preview & Screenshot Testing**: Write Compose `@Preview` annotations for all component variants and integrate automated screenshot testing (e.g. Paparazzi or Roborazzi) in GitHub Actions CI to catch visual regressions before code merges.
    4. **Version Catalog & Binary Distribution**: Package the design system within an internal Gradle version catalog (`libs.versions.toml`), allowing feature modules to consume design tokens with zero circular dependencies.

- **Q4: How does your background at Vectone Mobile, Ayla Networks, and Guardian directly prepare you for immediate impact at Outreach?**
  - *Model Answer*: At Vectone Mobile, I served as Mobile Lead for Worktual, an enterprise UCaaS calling and messaging platform, where I built VoIP/WebRTC calling, SIP signaling, and native telecom integrations—directly mirroring Outreach's voice dialer and telephony requirements. At Ayla Networks, I led mobile development for connected IoT platforms, architecting low-latency WebSocket communication and Room DB offline sync engines. At Guardian, I serve as Lead Mobile Engineer / Architect, establishing Clean Architecture, modularization, Jetpack Compose standards, and maintaining 99.85%+ crash-free reliability. I bring the technical depth in telecom, GraphQL, Compose, and Staff-level leadership Outreach requires.

---

## 4. STAR Stories Mapped to Past Career

### Story 1: Enterprise Architecture Overhaul & Crash-Free Reliability (Guardian)
- **Situation**: Guardian's enterprise mobile systems required higher stability, strict zero-trust security compliance, and sub-second startup times across a distributed enterprise user base.
- **Task**: Lead the architectural modernization of core Android applications and establish enterprise coding standards.
- **Action**: Spearheaded Clean Architecture refactoring with MVI unidirectional data flow; replaced volatile state mutations with Kotlin Coroutines StateFlow; enforced hardware-backed Keystore authorization; and integrated automated Baseline Profiles.
- **Result**: Reduced cold start latency by 35%, sustained 99.85%+ crash-free session rates, and passed enterprise security audits with zero findings.

### Story 2: Resilient Real-Time Bidirectional Sync & Offline Queues (Ayla Networks)
- **Situation**: High-frequency IoT device telemetry and commands faced packet drops and state desynchronization under fluctuating cellular networks.
- **Task**: Architect a resilient bidirectional telemetry and state synchronization pipeline.
- **Action**: Designed a WebSocket communication engine with auto-reconnection and exponential backoff; built transactional offline mutation queues in Room DB; and used WorkManager for reliable background syncing.
- **Result**: Delivered 100% telemetry data delivery with zero state loss and reduced device pairing dropouts by 25%.

### Story 3: Engineering Team Leadership & High-Concurrency UCaaS Telephony (Vectone Mobile)
- **Situation**: The Worktual communication app required high-concurrency real-time enterprise calling, SIP signaling, and messaging while facing UI responsiveness bottlenecks.
- **Task**: Lead a 10-developer engineering pod in Chennai to re-architect asynchronous data handling and optimize real-time VoIP performance.
- **Action**: Redesigned asynchronous event handling using Kotlin Coroutines and RxJava; integrated Android Telecom framework and ConnectionService for seamless call routing; and decoupled real-time WebRTC media streams from UI rendering.
- **Result**: Boosted UI responsiveness by 30%, supported thousands of simultaneous enterprise calls without ANRs, and delivered on-schedule milestone releases for enterprise clients.

---

## 5. Compensation Negotiation Script
> *"With 11+ years of software engineering expertise, verified experience leading mobile architecture at Guardian and Ayla Networks, hands-on production leadership architecting real-time enterprise voice calling and UCaaS platforms at Vectone Mobile, and specialized mastery of Kotlin, Jetpack Compose, Apollo GraphQL, and the Android Telecom framework, my target compensation is **₹41.5 LPA** (+48.2% hike on current 28 LPA baseline, well positioned within Outreach's Staff Software Engineer band in Hyderabad)."*