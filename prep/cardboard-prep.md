# Cardboard, Inc. — Interview Preparation Guide

**Target Role**: Product Engineer (Mobile Architecture & AI Video)  
**Location**: Bengaluru, Karnataka, India (On-site / Hybrid)  
**Target Compensation**: ₹38.0 LPA (+35.7% hike on current 28 LPA baseline, balanced with founding equity allocation)  

---

## 1. Interview Loop Structure & Evaluation Rubric
1. **Founder / Hiring Screen (30 mins)**: High-agency walkthrough of past 0-to-1 mobile products built, personal taste in mobile design and video software, experience building camera/video apps (Zero Cut, AvatarApp), motivation for joining a fast-paced YC-backed startup, and alignment with target compensation (₹38.0 LPA + equity).
2. **Product & Interaction Craft Pairing Session (60 mins)**: Live pairing session building a mobile UI component with high-fidelity gestures and animations (Jetpack Compose or SwiftUI). Evaluates attention to micro-interactions, frame budgets (<16ms), touch target physics, and state management.
3. **Mobile System Design: 4K/HDR Video Ingestion & Resumable Upload Engine (60 mins)**: Architecting the mobile video ingestion subsystem for Cardboard. Evaluates handling 1GB+ 4K HDR video files, hardware-accelerated thumbnail generation, background upload survival across app kills and Doze mode, and conversational AI agent streaming responses.
4. **Deep-Dive Technical & Concurrency Architecture (60 mins)**: Concurrency handling with Kotlin Coroutines/Flow, MediaCodec hardware decoding, WorkManager foreground workers, memory management when handling video frames in heap/native memory, and local SQLite/Room caching.
5. **Founding Team Alignment & Culture Fit (45 mins)**: Discussion with founders on velocity vs. craft, debugging hard undefined problems, autonomous decision-making, and leveraging AI coding tools to accelerate shipment velocity.

---

## 2. Mobile System Design Blueprint: Cardboard AI Video Ingestion & Conversational Agent Engine
- **Problem Statement**: Design the core client mobile architecture for Cardboard on iOS and Android. Mobile creators shoot 4K 60fps and 10-bit HDR video files (often 500MB to 5GB per clip). The mobile app must allow users to talk to the AI video editing agent, select/record raw footage, instantly generate local proxies/thumbnails without freezing the device, and execute rock-solid resumable background uploads that survive intermittent network drops, app backgrounding, and phone lock states.
- **Architectural Solution**:
  - **Decoupled Greenfield Architecture (`:app`, `:core:media`, `:core:uploader`, `:feature:agent`)**:
    - Unidirectional MVI architecture built with **Jetpack Compose** (Android) and **SwiftUI** (iOS).
    - Eliminates view state race conditions and ensures clean separation of media processing from conversational chat loops.
  - **Hardware-Accelerated Video Pipeline (`:core:media`)**:
    - Leverages Android `MediaCodec` and iOS `AVAsset` for hardware-accelerated video demuxing and thumbnail extraction directly from hardware surfaces without pulling raw uncompressed 4K bitmaps into JVM heap.
    - Generates lightweight proxy thumbnails (1080p / 720p) locally within 200ms so the user can interact and review edits instantaneously.
  - **Resumable Chunked Background Upload Engine (`:core:uploader`)**:
    - Adopts open chunked upload standards (TUS protocol or signed S3 multipart upload with 5MB-10MB chunk windows).
    - Each chunk calculates an MD5/SHA-256 checksum stored in an indexed **Room DB** transaction log.
    - Encapsulated within an Android `ForegroundService` backed by `WorkManager` with `OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST`, displaying an ongoing progress notification.
    - Survives app kills: On reboot or app relaunch, `WorkManager` queries the server for the latest byte offset and resumes seamlessly from the exact byte where it paused.
  - **Conversational Agent Interaction Loop (`:feature:agent`)**:
    - Real-time bidirectional streaming over WebSockets or HTTP/2 Server-Sent Events (SSE) for conversational AI responses.
    - Renders streaming text and timeline edit suggestions with zero UI thread contention using conflated Kotlin StateFlows.

---

## 3. Deep-Dive Technical Q&A

- **Q1: How do you upload multi-gigabyte 4K HDR phone videos reliably when the user locks their phone or switches to Instagram?**
  - *Model Answer*: 
    1. **Chunked Resumable Upload Protocol (TUS / S3 Multipart)**: We divide large files into immutable chunks (typically 5MB). The client creates an upload session on the server and receives an upload URL. Each chunk is uploaded with a `Content-Range` header.
    2. **State Persistence**: We persist the upload state machine in a local database (`Room DB`), tracking `fileUri`, `totalBytes`, `uploadedBytes`, `chunkIndex`, and `sessionUrl`.
    3. **Background Execution via WorkManager**: We wrap the upload worker in Android `CoroutineWorker` configured with `setForeground(ForegroundInfo(notificationId, notification))` before initiating uploads. This promotes the worker to a foreground service, preventing Android from throttling network sockets or killing the process.
    4. **Network & Connectivity Adaptation**: We bind the `OneTimeWorkRequest` with `Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build()`. When connectivity drops, WorkManager pauses and triggers automatic retry with exponential backoff and jitter. Upon reconnecting, the worker performs a `HEAD` request to query the server's byte offset and resumes without re-transmitting already received chunks.

- **Q2: Handling 4K video frames can quickly trigger Out-Of-Memory (OOM) errors on mobile devices. How do you manage memory and surface rendering?**
  - *Model Answer*: 
    1. **Never Decode Uncompressed Bitmaps to JVM Heap**: A single uncompressed 4K frame (3840x2160 in ARGB_8888) consumes ~33MB of memory. Decoding just 10 frames into the JVM heap will exhaust the app's heap space and crash.
    2. **Hardware Surfaces (`SurfaceView` / `TextureView`)**: Feed video decoders directly into hardware `Surface` buffers using `MediaCodec` or `ExoPlayer`, completely bypassing the Java/Kotlin heap.
    3. **Downsampled Thumbnails**: When generating scrub previews, use `MediaMetadataRetriever` with `OPTION_CLOSEST_SYNC` combined with `inSampleSize` downsampling (e.g., target 320x180 resolution) to ensure thumbnail bitmaps consume <250KB each.
    4. **Glide / Coil Memory Caching**: Use an LRU memory cache with a strict budget (max 20% of available memory) and disk caching for scrub bar filmstrips.

- **Q3: How do you ensure the conversational AI agent chat and dynamic timeline UI maintain buttery 60fps/120fps fluid scrolling during live video playback?**
  - *Model Answer*: 
    1. **Decoupled State Architecture**: The conversational chat stream (LLM tokens arriving at 20-50 tokens/sec) and the video playback timeline (emitting playhead updates at 60Hz) operate on separate reactive state holders.
    2. **Compose Recomposition Optimization**: Mark all state models with `@Immutable` or `@Stable`. Use `derivedStateOf` for playhead scrubber calculations so only the scrubber thumb recomposes rather than the entire timeline track.
    3. **Conflated Flow for Streaming Tokens**: Buffer incoming streaming LLM tokens using Kotlin `Flow.conflate()` or chunk updates into 50ms UI render batches, preventing rapid-fire recomposition storms on the main thread.
    4. **Off-Thread Markdown/Rich Text Parsing**: Parse incoming markdown tokens and syntax highlighting on `Dispatchers.Default`, passing pre-computed `AnnotatedString` structures to the Compose UI.

- **Q4: How does your experience building Zero Cut and AvatarApp position you to build Cardboard's mobile product?**
  - *Model Answer*: I have built and published mobile video and camera applications from scratch. With **Zero Cut — One-Take Studio**, I implemented real-time on-device neural video segmentation using TensorFlow Lite and OpenGL shaders, allowing creators to produce continuous virtual studio recordings without post-production latency. With **AvatarApp**, I built an offline camera-to-avatar pipeline using CameraX, OpenCV, and ML Kit. Combined with my 11+ years leading mobile architecture at Guardian and Ayla Networks, I know how to pair deep media engineering with high-velocity product craft to take Cardboard from v1 to millions of daily creators.

---

## 4. STAR Stories Mapped to Past Career

### Story 1: Real-Time Mobile Video & AI Segmentation Architecture (Zero Cut / Infitech)
- **Situation**: Mobile creators needed a way to produce studio-grade video recordings without complex desktop Chroma key post-production equipment.
- **Task**: Architect an on-device video application capable of performing real-time background segmentation and composite rendering at 30fps without overheating the phone.
- **Action**: Built an end-to-end media pipeline combining **CameraX**, **OpenGL ES 2.0/3.0 shaders**, and an optimized **TensorFlow Lite** neural model; engineered double-buffered GPU texture surfaces to avoid CPU-GPU memory copy bottlenecks; and tuned thread priority to eliminate camera stutter.
- **Result**: Achieved real-time 30fps segmentation on mid-range Android devices, eliminated rendering latency, and published a working product for content creators.

### Story 2: Resilient Offline Caching & Telemetry Synchronization (Ayla Networks)
- **Situation**: Connected devices frequently operated in weak cellular and Wi-Fi environments, resulting in dropped telemetry payloads and desynchronized state.
- **Task**: Engineer a bulletproof offline-first transaction and event queue on mobile clients.
- **Action**: Designed an offline transactional database layer using **Room DB**; implemented chunked event buffering with automatic exponential retry backoff; and synchronized data over persistent **WebSockets** with automated heartbeat reconnection.
- **Result**: Guaranteed 100% telemetry delivery during network drops and reduced device onboarding failures by 25%.

### Story 3: High-Scale Engineering Pod Leadership & Reactive Modernization (Vectone Mobile)
- **Situation**: The Worktual unified communications application suffered from UI sluggishness when simultaneous video feeds, chat updates, and signaling events arrived.
- **Task**: Re-architect the client-side concurrency and state orchestration for a team of 10 developers.
- **Action**: Spearheaded migration to **Kotlin Coroutines** and **RxJava**; decoupled real-time WebRTC media streams from UI rendering; and instituted strict code review and CI automated testing standards.
- **Result**: Boosted UI responsiveness by 30%, supported high-concurrency enterprise video calls with zero ANRs, and delivered on-schedule releases.

---

## 5. Compensation Negotiation Script
> *"With 11+ years of software engineering expertise, verified track record leading mobile architecture at Guardian and Ayla Networks, and my specialized hands-on experience building on-device video, camera, and AI applications (Zero Cut, AvatarApp, OpenCV/TensorFlow), my target compensation is **₹38.0 LPA** (+35.7% hike on current 28 LPA baseline, well balanced with a meaningful founding-team equity allocation at Cardboard, Inc.)."*
