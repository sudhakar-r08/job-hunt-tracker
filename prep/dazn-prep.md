# DAZN — Interview Preparation Guide

**Target Role**: Lead Software Engineer / Android Architect  
**Location**: Hyderabad, Telangana, India (Hybrid)  
**Target Compensation**: ₹38.0 LPA (+35.7% hike on current 28 LPA baseline)  

---

## 1. Interview Loop Structure & Evaluation Rubric
1. **Recruiter Screen (30 mins)**: Career journey, experience leading mobile architecture for high-concurrency client platforms, notice period (90 days, negotiable), and alignment with DAZN's global sports entertainment footprint.
2. **Android Architecture & Video Systems Design (60 mins)**: Staff/Principal Mobile Architect — Design a high-concurrency live sports streaming Android client (Mobile & Android TV) supporting millions of simultaneous viewers, low-latency live streaming (LL-HLS/DASH), multi-track audio/subtitles, DRM, and real-time interactive overlay synchronisation (live scores, stats, fan polls via WebSockets).
3. **Advanced Kotlin, Concurrency & Media Coding (60 mins)**: Lead Engineer — Live Kotlin coding session focused on thread-safe media buffer management, Coroutine StateFlow pipelines, custom ExoPlayer analytics listeners, and memory optimization to prevent frame skips during high-frame-rate (60fps) video playback.
4. **Behavioral, Engineering Leadership & Cultural Fit (45 mins)**: Engineering Director / VP — Mentoring distributed squads, resolving architectural disagreements, driving cross-functional alignment with backend video encoding and CDN teams, and handling high-stakes live matchday outages.

---

## 2. Mobile System Design Blueprint: Ultra-Low Latency Live Sports Streaming & Interactive Telemetry Client
- **Problem**: Build a resilient, high-performance Android live sports streaming application that streams broadcast-grade 1080p/4K 60fps video with sub-3-second latency, maintaining seamless playback across fluctuating network conditions while overlaying real-time match telemetry (live goals, player stats, commentary) without UI frame drops.
- **Architectural Solution**:
  - **Player & Media Engine**:
    - Build on **AndroidX Media3 (ExoPlayer)** hosted inside a dedicated foreground `MediaSessionService` to ensure background audio survival and system-wide media controls.
    - Implement custom `LoadControl` with dynamic buffer sizing: keep 2–3s buffer during low-latency live streaming (LL-HLS / CMAF chunks) to minimize latency, but automatically expand buffer to 10–15s during jitter to prevent stall underruns.
    - Leverage hardware-accelerated decoders (`MediaCodec`) with surface view rendering (`SurfaceView` over `TextureView` for 30% GPU power savings and zero visual stutter).
  - **Real-Time Interactive Telemetry Pipeline**:
    - Multiplex live scoreboards, match events, and interactive polls over a persistent **WebSocket** connection.
    - Timestamp-align incoming telemetry payloads with video playback clock using `MediaItem` presentation timestamps (PTS / ID3 timed metadata).
    - Expose telemetry through a conflated `StateFlow` stream consumed by a declarative **Jetpack Compose** HUD overlay. Compose layout passes bypass video rendering surfaces to guarantee rock-solid 60fps UI performance.
  - **Multi-Module Clean Architecture**:
    - `:core:player` (abstract player interface, ExoPlayer implementation, DRM license management).
    - `:core:network` (OkHttp, WebSockets, CDN edge token rotation).
    - `:feature:stream` (live stream UI, Jetpack Compose overlays, Android TV D-pad navigation).
    - `:feature:stats` (real-time telemetry and match timeline).
  - **DRM & Multi-Bitrate ABR**:
    - Modular DRM integration with Widevine Modular DRM (L1 hardware-backed where supported, L3 fallback).
    - Dynamic adaptive bitrate (ABR) algorithm tailored for live sports: prioritize frame rate preservation (60fps) over pure resolution during high-motion action scenes.

---

## 3. Deep-Dive Technical Q&A

- **Q1: How do you prevent video player stalls and frame stutter during live sports streams over unreliable mobile networks?**
  - *Model Answer*: Live sports requires balancing latency against playback continuity. I configure a custom `DefaultLoadControl` in ExoPlayer with tailored `minBufferMs` (2,500ms) and `maxBufferMs` (10,000ms), paired with an adaptive `TrackSelection.Factory` that monitors both network bandwidth throughput and video decoder frame-drop metrics. When network conditions degrade, the ABR controller shifts to lower bitrate video variants before audio or video buffers starve. For rendering, using `SurfaceView` allows direct hardware compositing to the display pipeline, eliminating the memory copy overhead of `TextureView` and preventing UI thread stutter.

- **Q2: How do you synchronize live match telemetry (such as a goal notification or live player stats) with video playback without spoiling the play?**
  - *Model Answer*: Video streams experience CDN latency and local playback buffering delays (typically 2 to 6 seconds behind absolute real-time), whereas WebSockets deliver telemetry almost instantly. To prevent spoiling the goal before the video displays it, the backend injects presentation timestamps (PTS) or ID3 timed metadata into the video chunk headers. The WebSocket telemetry messages carry corresponding match-clock timestamps. The client buffers the telemetry in a priority queue and only dispatches the state event to the UI when the player's current playback position (`player.currentPosition`) matches the telemetry timestamp.

- **Q3: How does your background at Vectone Mobile and Ayla Networks prepare you for DAZN?**
  - *Model Answer*: At Vectone Mobile, I led the Android architecture for the Worktual UCaaS platform, managing high-concurrency real-time video/audio conferencing using WebRTC, SIP, and custom jitter buffer synchronization across 10-developer pods. At Ayla Networks, I built real-time WebSocket state synchronization pipelines for enterprise IoT connected devices with sub-100ms latency. At Guardian, I lead enterprise mobile architecture, enforcing Clean Architecture, modularity, and 99.8%+ crash-free sessions. This gives me the exact technical intersection needed for DAZN: deep real-time media networking, robust Android internals, and proven architectural leadership.

- **Q4: How do you architect an Android codebase to support both Mobile (touch) and Android TV (D-pad focus navigation)?**
  - *Model Answer*: I separate the presentation and input handling layers from the core domain and playback business logic using multi-module Clean Architecture. The `:core:player` and `:feature:stream:domain` modules remain 100% platform-agnostic. For the UI layer, Jetpack Compose enables shared state models while tailoring layout and focus navigation. On Android TV, we leverage Compose for TV (`androidx.tv.material3`) and configure explicit focus requesters (`FocusRequester`, `Modifier.focusable()`) and D-pad directional traversal, while mobile leverages standard touch gestures and picture-in-picture (PiP).

---

## 4. STAR Stories Mapped to Past Career

### Story 1: Eliminating Real-Time Media Latency & Frame Lag (Vectone Mobile)
- **Situation**: In the Worktual enterprise unified communications application, high-concurrency video and VoIP calls experienced noticeable jitter, audio/video synchronization drift, and UI frame freezes during network handoffs.
- **Task**: Overhaul the media playback and network transport architecture to achieve seamless, low-latency communication.
- **Action**: Segregated audio/video decoding and network packet processing onto dedicated priority threads; re-architected asynchronous state management using Kotlin Coroutines and RxJava; optimized buffer sizing to dynamically adapt to packet loss without overflowing client memory.
- **Result**: Reduced call audio/video dropouts by 42%, improved connection setup latency by 30%, and sustained 99.6% crash-free sessions across 100K+ enterprise users.

### Story 2: Resilient Real-Time Bidirectional Event Streaming (Ayla Networks)
- **Situation**: Enterprise IoT platform needed to deliver continuous live device telemetry and receive instant commands across fluctuating cellular and Wi-Fi networks.
- **Task**: Architect a real-time bidirectional messaging pipeline that guarantees message delivery and immediate UI reactivity without battery drain.
- **Action**: Built a WebSocket communication layer with automated exponential backoff reconnection, heartbeat monitors, and local Room DB write-ahead logging; decoupled high-frequency network packets from the UI thread using Kotlin Flow conflation.
- **Result**: Achieved sub-100ms command latency, reduced pairing/telemetry dropouts by 25%, and preserved battery life across 50+ diverse OEM Android devices.

### Story 3: Enterprise Modularization & Quality Governance (Guardian)
- **Situation**: Monolithic mobile client architecture caused high build times, regression risks across distributed feature pods, and inconsistent architectural patterns.
- **Task**: Establish enterprise-wide mobile architectural standards, Clean Architecture modularization, and strict quality gates.
- **Action**: Led architectural decomposition into isolated multi-modules (core, domain, data, feature); instituted automated CI/CD linting, static analysis, and code quality governance; mentored 15+ mobile developers across distributed pods.
- **Result**: Cut developer build times by 35%, eliminated architectural coupling, and achieved a 99.8%+ crash-free session rate across production releases.

---

## 5. Compensation Negotiation Script
> *"With 11+ years of progressive software engineering expertise, verified experience leading high-throughput real-time communications and media architecture at Guardian, Ayla Networks, and Vectone Mobile, and my specialized ability to architect scalable live streaming and telemetry systems on Android, my target compensation is **₹38.0 LPA** (+35.7% hike on current 28 LPA baseline, well within DAZN's ₹36–45 LPA Staff/Lead engineering band)."*
