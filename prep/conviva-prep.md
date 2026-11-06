# Conviva — Interview Preparation Guide

**Target Role**: Senior Engineer - Android (Mobile & Smart TV Telemetry SDK)  
**Location**: Bengaluru, Karnataka, India (77 Town Centre / Hybrid)  
**Target Compensation**: ₹38.5 LPA (+37.5% hike on current 28 LPA baseline, well positioned within Conviva's senior engineering band in Bengaluru)  

---

## 1. Interview Loop Structure & Evaluation Rubric
1. **Recruiter / Screening Round (30 mins)**: High-level career overview, deep dive into past SDK development experience (Ayla Mobile SDK, Guardian Security Foundations), familiarity with media streaming (ExoPlayer/WebRTC), hybrid work model at 77 Town Centre Bengaluru, notice period (90 days, negotiable), and alignment with target compensation (₹38.5 LPA).
2. **Technical Screen / Live Coding & Data Structures (60 mins)**: HackerRank / CoderPad live coding in Kotlin/Java. Evaluates algorithms, thread safety, high-throughput in-memory buffering, concurrency primitives (ConcurrentLinkedQueue, Atomic primitives, Mutex, Coroutine Channels), and error handling under memory pressure.
3. **Android SDK Architecture & Media Telemetry Deep Dive (60 mins)**: Principal / Staff Engineer — Evaluates public SDK ergonomics, binary footprint minimization (<1.5MB AAR budget), avoiding transitive dependency conflicts, hooking into ExoPlayer / Media3 player lifecycles, measuring video QoE metrics (re-buffering, time-to-first-frame, bitrate adaptation), and Android TV / Fire TV lifecycle quirks.
4. **Mobile System Design: Large-Scale Telemetry & Analytics SDK (60 mins)**: Engineering Director / Architect — Design an end-to-end client telemetry engine collecting billions of real-time events across mobile and smart TV clients with offline buffering, batch dispatch, network throttling adaptation, and zero UI thread interference.
5. **Engineering Craft, Culture & Leadership (45–60 mins)**: Engineering Manager — Collaboration with global integration teams, troubleshooting customer-facing SDK integration bugs, balancing SDK feature requests vs. binary size budgets, and mentoring junior engineers.

---

## 2. Mobile System Design Blueprint: Conviva Real-Time Video & AI Agent Telemetry SDK
- **Problem Statement**: Architect a lightweight, high-performance Android SDK (`ConvivaCoreSDK`) deployed across mobile, Android TV, and Fire TV streaming applications. The SDK must non-intrusively intercept video playback events (playback start, stalls, bitrate shifts, seek operations, ad breaks) and app/agent interactions, stage high-frequency telemetry in an in-memory lock-free buffer, compress and dispatch payloads in micro-batches to Conviva collectors, and guarantee zero main-thread jank (<0.1ms overhead per event) and zero app crashes.
- **Architectural Solution**:
  - **Player Instrumentation Layer (`:sdk:media-tracker`)**:
    - Registers non-intrusive listeners with media players (`Player.Listener` in AndroidX Media3 / ExoPlayer).
    - Captures state transitions: `STATE_BUFFERING`, `STATE_READY`, `STATE_ENDED`, `onPlaybackStateChanged`, `onVideoSizeChanged`, `onTracksChanged`.
    - Computes microsecond-accurate metrics: Time-to-First-Frame (TTFF), Rebuffer Ratio (`rebufferDuration / totalPlayDuration`), Average Bitrate, and Seek Latency without polling.
  - **High-Throughput Lock-Free Telemetry Pipeline (`:sdk:core`)**:
    - Incoming telemetry events are staged in a lock-free ring buffer (`RingBuffer` or `ConcurrentLinkedQueue`) with strict capacity limits (e.g., 2,000 events) to prevent Out-Of-Memory (OOM) scenarios.
    - Worker thread scheduled via Kotlin Coroutines on a dedicated single-threaded dispatcher (`Dispatchers.IO.limitedParallelism(1)`) or background handler thread drains the buffer.
  - **Dynamic Batching & Compression Dispatcher (`:sdk:network`)**:
    - Adaptive batch flush trigger: whichever comes first—buffer reaches 50 events OR timer reaches 3 seconds.
    - Chunks are compressed using Gzip in-memory before transmission, reducing network payload size by 75%.
    - Transmitted via raw lightweight HTTP/2 client (`HttpURLConnection` or encapsulated shaded OkHttp) to avoid conflicting with host application dependency versions.
  - **Offline Caching & Network Adaptation (`:sdk:persistence`)**:
    - During network loss, events stage to a lightweight SQLite/Room cache with a rolling FIFO eviction policy (max 10MB disk quota).
    - Backpressure engine dynamically drops non-critical debug telemetry if network latency spikes, preserving primary QoE metrics.
  - **Form-Factor Adaptability (Mobile vs. Android TV vs. Fire OS)**:
    - Android TV / Fire TV: Detects D-pad navigation, Leanback UI states, and strict memory limits (low-RAM devices with 1GB total heap).
    - Employs strict memory pooling to eliminate object allocation churning in inner loops, keeping Garbage Collection (GC) pauses near zero.

---

## 3. Deep-Dive Technical Q&A

- **Q1: In public SDK development, how do you prevent classpath conflicts and transitive dependency collisions with host applications?**
  - *Model Answer*: 
    1. **Zero External Dependencies**: Strive for pure Kotlin/Java standard library and core Android platform APIs for fundamental SDK capabilities.
    2. **Dependency Shading & Namespace Relocation**: If an external library (like OkHttp, Protobuf, or Gson) is essential, use Gradle Shadow Plugin (`com.github.johnrengelman.shadow`) to relocate the package namespace (e.g., `com.squareup.okhttp3` ➔ `com.conviva.internal.okhttp3`). This isolates the SDK's dependencies entirely from the host app's classpath.
    3. **Consumer Proguard Rules**: Ship `consumerProguardFiles` inside the AAR that keep only public API entry points while shrinking and obfuscating all internal helper classes.
    4. **No Static Singletons with Global State**: Expose client instances via explicit builder/factory patterns (`ConvivaAnalytics.create(context, config)`) tied to the application lifecycle rather than leaking hidden process-level singletons.

- **Q2: How do you instrument ExoPlayer / AndroidX Media3 to measure Time-to-First-Frame (TTFF) and playback re-buffering without inducing UI thread stutter?**
  - *Model Answer*: 
    1. **Hook into Media3 Listeners**: Attach an analytics listener implementing `AnalyticsListener` or `Player.Listener`.
    2. **TTFF Calculation**: Record monotonic timestamp `t_init = SystemClock.elapsedRealtime()` when `player.prepare()` or `play()` is called. In `onRenderedFirstFrame(EventTime eventTime, Output output)`, capture `t_first = SystemClock.elapsedRealtime()`. The difference `(t_first - t_init)` yields exact TTFF.
    3. **Re-buffering Tracking**: In `onPlaybackStateChanged(int state)`, when transitioning from `STATE_READY` with `playWhenReady == true` to `STATE_BUFFERING`, record `stallStart = SystemClock.elapsedRealtime()`. When transitioning back to `STATE_READY`, record `stallEnd` and accumulate `totalStallTime += (stallEnd - stallStart)`.
    4. **Off-Thread Dispatch**: Inside listener callbacks (which execute on the player thread/Main thread), package event metadata into a pre-allocated POJO and immediately push it into a thread-safe ring buffer (`buffer.offer(event)`). The call takes <5 microseconds and never performs disk I/O, string formatting, or network calls on the main thread.

- **Q3: Android TV and Amazon Fire TV devices often operate on heavily constrained hardware (quad-core ARM, 1GB RAM). How do you ensure the SDK does not trigger Out-Of-Memory (OOM) errors or ANRs?**
  - *Model Answer*: 
    1. **Object Pooling**: Re-use telemetry event objects (`Pool<TelemetryEvent>`) to minimize object allocations during continuous playback, eliminating garbage collection (GC) churn and frame jank.
    2. **Bounded Buffers**: Set a hard ceiling on queue size (e.g., 500 events on low-RAM devices). If the queue fills (e.g., device offline for extended periods), drop low-priority telemetry (heartbeats, debug logs) using FIFO eviction while strictly preserving critical session lifecycle markers.
    3. **Background Priority Scheduling**: Execute background processing on low-priority worker threads (`Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND)`) to guarantee the streaming player's audio/video decoders maintain 100% CPU priority.
    4. **Memory Trimming**: Register `ComponentCallbacks2` and listen for `onTrimMemory(level)`. Under `TRIM_MEMORY_RUNNING_CRITICAL`, immediately flush or discard in-memory buffers to prevent OS process termination.

- **Q4: How does your track record at Guardian, Ayla Networks, and Vectone Mobile prepare you to step in as a Senior Android Engineer at Conviva?**
  - *Model Answer*: At Ayla Networks, I led mobile development for high-scale connected device platforms and engineered the core Ayla Mobile SDK. I designed real-time telemetry streaming over WebSockets, optimized Room DB offline event persistence, and solved complex BLE/Wi-Fi connection state machines. At Vectone Mobile, I served as Mobile Lead for the Worktual UCaaS communications app, managing real-time WebRTC media pipelines, audio/video streaming, and low-latency packet transmission. At Guardian, I serve as Lead Mobile Engineer / Architect, establishing Clean Architecture and maintaining 99.85%+ crash-free reliability across enterprise fleets. This exact combination of SDK architecture, real-time media streaming, and production client resilience directly mirrors Conviva's mission.

---

## 4. STAR Stories Mapped to Past Career

### Story 1: Enterprise Mobile SDK Architecture & Telemetry Optimization (Ayla Networks)
- **Situation**: The Ayla Mobile SDK suffered from large binary footprint, excessive memory allocation, and connection drops during continuous telemetry transmission from IoT appliances.
- **Task**: Re-architect the core mobile SDK to create a modular, lightweight library with reliable background telemetry dispatch.
- **Action**: Decomposed the SDK into decoupled modules (`:sdk-core`, `:sdk-telemetry`, `:sdk-ble`); implemented an in-memory lock-free circular buffer for high-frequency events; and batched telemetry payloads with Gzip compression over WebSockets with exponential backoff reconnects.
- **Result**: Reduced SDK binary size by 35%, lowered background memory overhead by 40%, and achieved 99.9% data delivery reliability across millions of connected customer devices.

### Story 2: Real-Time Media Streaming & Performance Optimization (Vectone Mobile)
- **Situation**: The Worktual unified communications application experienced audio/video stutter, UI frame drops, and occasional ANRs when handling high-concurrency real-time calls.
- **Task**: Re-engineer the media transmission layer and asynchronous event pipeline to ensure smooth 60fps UI responsiveness during active calls.
- **Action**: Decoupled WebRTC media engine signaling from the main thread; re-architected reactive event handling using Kotlin Coroutines and StateFlow; and implemented jitter buffer telemetry to monitor network packet loss in real time.
- **Result**: Boosted app responsiveness by 30%, eliminated ANRs during active calls, and maintained seamless high-definition media sessions for enterprise clients.

### Story 3: Client Stability Governance & Startup Optimization (Guardian)
- **Situation**: Guardian's enterprise client applications required sub-second launch times and stringent 99.8%+ crash-free session rates for enterprise compliance.
- **Task**: Lead architectural refactoring and enforce rigorous performance quality gates across distributed feature teams.
- **Action**: Implemented Android Baseline Profiles to pre-compile hot execution paths; instituted automated CI/CD performance regression gates and LeakCanary memory checks; and governed multi-module Clean Architecture standards.
- **Result**: Decreased cold start latency by 35%, eliminated memory leaks, and maintained a verified 99.85%+ crash-free session rate across enterprise users.

---

## 5. Compensation Negotiation Script
> *"With 11+ years of software engineering expertise, verified experience leading mobile architecture and SDK development at Guardian and Ayla Networks, and extensive hands-on proficiency in real-time media streaming (WebRTC, ExoPlayer), low-overhead telemetry pipelines, and Android TV/mobile platforms, my target compensation is **₹38.5 LPA** (+37.5% hike on current 28 LPA baseline, perfectly positioned within Conviva's senior engineering band in Bengaluru)."*
