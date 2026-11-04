# Bjak — Interview Preparation Guide

**Target Role**: Mobile Application Developer (Android & AI Finance Agent)  
**Location**: Remote, India (Bangalore / Chennai / Hyderabad)  
**Target Compensation**: ₹38.5 LPA (+37.5% hike on current 28 LPA baseline)  

---

## 1. Interview Loop Structure & Evaluation Rubric
1. **Online Assessment / Practical Coding Task (Take-home or Live)**: Rapid implementation of a clean, performant Android feature in Kotlin. Evaluates Clean Architecture, MVI/MVVM separation, Jetpack Compose UI ergonomics, error handling, loading states, and automated unit test coverage. (Tip: Ship within 24–48 hours to signal high velocity and ownership).
2. **Role-Specific Technical Deep-Dive & Architecture (60 mins)**: Senior Engineering Lead — Deep dive into Android fundamentals, Kotlin Coroutines/Flow, memory management, offline-first data caching with Room, and integrating on-device AI/ML models (**TensorFlow Lite**) to power Bjak’s AI Finance Agent.
3. **CEO / Final Culture Round (30–45 mins)**: CEO / Co-founder — Product mindset, thinking in end-to-end user journeys rather than just screens, customer empathy in simplifying complex insurance/finance, startup speed, and personal accountability.

---

## 2. Mobile System Design Blueprint: Bjak AI Finance Agent & Instant Claims Engine
- **Problem**: Build a lightning-fast native Android application where users interact with an AI Finance Agent to compare insurance policies, manage renewals, and submit instant claims (including on-device document OCR and accident damage assessment) with zero lag, instant responsiveness, and guaranteed transaction reliability.
- **Architectural Solution**:
  - **On-Device AI Inference Engine (`:core:ai`)**:
    - Load quantized **TensorFlow Lite (`.tflite`)** models using the `org.tensorflow:tensorflow-lite` runtime with GPU / NNAPI delegate acceleration.
    - Pre-process camera bitmaps on a background coroutine (`Dispatchers.Default`) via `Bitmap.createScaledBitmap` and normalized `ByteBuffer` arrays to ensure the main UI thread never drops a single frame (sub-16ms budget).
    - Run edge document verification (driver license, vehicle registration, receipt OCR) locally, returning instant confidence scores before cloud synchronization.
  - **Reactive State Machine & Jetpack Compose (`:feature:agent`)**:
    - Implement an MVI architecture where user financial intent produces unidirectional state streams (`Intent` ➔ `Processor` ➔ `StateFlow<AgentViewState>`).
    - Use `@Immutable` data classes and `derivedStateOf` in Compose to isolate recompositions so only updated card components re-render during live quote calculations.
  - **Idempotent Transaction & Offline Sync (`:core:finance`)**:
    - Wrap insurance policy purchases and payment submissions in an idempotent transaction state machine backed by local **Room DB** with unique client-generated UUID keys.
    - If the user loses network during payment verification, a dedicated `WorkManager` worker reconciles payment gateway webhooks automatically upon reconnection.

---

## 3. Deep-Dive Technical Q&A

- **Q1: How do you integrate and optimize a TensorFlow Lite model on Android without degrading app launch time or causing frame drops?**
  - *Model Answer*: 
    1. **Asynchronous Model Initialization**: Never load model buffers on the main thread during app launch. Initialize the `Interpreter` lazily in a background coroutine using `Dispatchers.IO` with memory-mapped buffers (`FileChannel.map()`), which avoids copying the model into Java heap space.
    2. **Hardware Acceleration**: Configure `GpuDelegate` or `NnApiDelegate` based on device capability, with a graceful fallback to CPU multi-threading (`setNumThreads(4)`).
    3. **Bitmap Normalization**: Run image resizing and pixel array conversions on `Dispatchers.Default`. Reuse input/output `ByteBuffer` allocations across inference passes to avoid triggering garbage collection (GC) pauses during camera streams.

- **Q2: How do you design user-facing financial flows (payments, insurance binding) to be completely tamper-resistant and resilient to network loss?**
  - *Model Answer*: Financial operations require determinism and idempotency. Every critical submission generates an `idempotency_key` (UUIDv4) stored alongside the transaction state in an encrypted local Room DB (via SQLCipher). Requests are dispatched with exponential backoff retry. If the app gets terminated or the network flutters mid-flight, the app polls the transaction status using the idempotency key rather than submitting a duplicate charge. For security, sensitive tokens are stored in the hardware-backed Android Keystore with BiometricPrompt authorization, and network requests enforce TLS 1.3 certificate pinning.

- **Q3: What distinguishes your approach to Jetpack Compose from ordinary Android developers?**
  - *Model Answer*: I architect Compose for 60fps/120fps predictability. I ensure view model state objects are strictly `@Immutable`, pass lambdas rather than raw states down into deep leaf composables, and leverage `Modifier.drawWithContent` for custom animations to skip layout and measurement phases. Furthermore, I inspect recomposition counters in the Layout Inspector and run Macrobenchmark tests to ensure baseline profiles pre-compile critical execution paths, achieving sub-600ms cold starts.

- **Q4: How does your background at Infitech Reality and Guardian make you the ideal builder for Bjak's AI Finance Agent?**
  - *Model Answer*: At Infitech Reality, I led hands-on integration of on-device machine learning models using TensorFlow Lite and OpenCV for real-time edge computer vision and document recognition, mastering native NDK/JNI bindings and memory optimization. At Guardian, I lead mobile architecture for high-concurrency enterprise applications, enforcing Clean Architecture, strict security, and maintaining 99.8%+ crash-free session rates. This gives me both the specialized on-device AI engineering skills and the architectural maturity required to build Bjak’s flagship mobile experience.

---

## 4. STAR Stories Mapped to Past Career

### Story 1: On-Device Neural Vision & Document Parsing on Edge (Infitech Reality)
- **Situation**: Client applications required real-time document and license plate recognition in poor network environments where cloud API latency was unacceptable.
- **Task**: Implement on-device machine learning inference running fully offline with sub-200ms detection speed.
- **Action**: Converted and quantized trained neural models to TensorFlow Lite; engineered native C++ pre-processing bindings via NDK/JNI; and decoupled camera frame acquisition (CameraX) from inference execution using coroutine channels.
- **Result**: Achieved 94% on-device recognition accuracy in under 180ms without consuming cloud bandwidth or leaking sensitive user document images.

### Story 2: Achieving 99.8%+ Crash-Free Reliability & Frame Performance (Guardian)
- **Situation**: Legacy mobile modules suffered from sporadic memory leaks, state desynchronization, and UI stutter during complex user flows.
- **Task**: Overhaul application architecture to achieve top-tier enterprise stability and buttery-smooth user experience.
- **Action**: Spearheaded Clean Architecture refactoring with MVI unidirectional data flow; replaced error-prone state mutations with Kotlin Coroutines StateFlow; profiled memory with LeakCanary and Android Studio Profiler; and established automated CI quality gates.
- **Result**: Sustained 99.8%+ crash-free session rate across hundreds of thousands of users and reduced cold start latency by 35%.

### Story 3: Real-Time State Management & UI Responsiveness (Vectone Mobile)
- **Situation**: The Worktual communication app suffered from UI freezes when concurrent VoIP signaling, chat messages, and network status updates collided on the main thread.
- **Task**: Redesign asynchronous state propagation to ensure zero UI frame drops.
- **Action**: Decoupled network and signaling events onto background dispatchers; implemented custom reactive operators to conflate rapid state updates; and moved complex list rendering to lightweight recycled view holders with diffing.
- **Result**: Boosted UI responsiveness by 30%, eliminated ANRs, and supported thousands of simultaneous enterprise calls.

---

## 5. Compensation Negotiation Script
> *"With 11+ years of software engineering expertise, verified experience leading mobile architecture at Guardian and Ayla Networks, and my specialized hands-on track record building on-device TensorFlow Lite AI models and high-performance Kotlin/Compose applications, my target compensation is **₹38.5 LPA** (+37.5% hike on current 28 LPA baseline, well aligned with Bjak's top-tier engineering talent band in India)."*
