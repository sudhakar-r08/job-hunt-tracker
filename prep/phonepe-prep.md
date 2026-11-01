# Interview Preparation Guide — PhonePe
**Role**: Android Developer (Staff / Senior Mobile Architecture Band)
**Job ID**: `1000000000003916` | **Location**: Bengaluru, Karnataka

---

## 1. Role & Engineering Culture Context
- **Product**: PhonePe's flagship financial & UPI super-app serving 500M+ users across payments, wealth, insurance, and merchant commerce.
- **What PhonePe Tests Rigorously**:
  1. **Machine Coding / Low-Level Design (LLD) in Kotlin** (90–120 mins: clean, extensible, thread-safe Android/Kotlin architecture).
  2. **Android Internals, Concurrency & Memory Management** (Looper/Handler, Binder IPC, OOM prevention, Cold Start time `<400ms`, ANR elimination).
  3. **Mobile System Design (HLD)** (Offline-first reliability, cryptographic security, multi-module build scalability).

---

## 2. Mobile System Design Scenario
### **Prompt**: *"Design the PhonePe UPI Transaction Status & History Sync Engine for flaky 2G/edge networks."*
- **Key Architectural Pillars to Present**:
  1. **Idempotency & State Machine**:
     - Every payment intent generates a client-side UUID idempotency key (`CREATED -> INITIATED -> PENDING_NPCI -> SUCCESS / FAILED`).
  2. **Dual-Channel Status Resolution (Push + Smart Polling)**:
     - Primary: High-priority FCM data message triggers background `WorkManager` / foreground sync.
     - Fallback: Exponential backoff polling (`2s, 4s, 8s, 16s`) when push is delayed on restricted OEM ROMs (Xiaomi/Vivo/Oppo).
  3. **Security & Tamper Resistance**:
     - Hardware-backed **Android Keystore**, Play Integrity API, TLS 1.3 Certificate Pinning with backup pins, SQLCipher encrypted Room DB.
  4. **Cold Start & APK Size Optimization**:
     - R8 full mode, Baseline Profiles, App Startup library (lazy initialization of heavy SDKs), dynamic feature / multi-module Gradle graph.

---

## 3. High-Probability Technical Questions
1. **Android Internals**: *"How do you debug and eliminate ANRs (Application Not Responding) in production?"*
   - **Your Answer**: Analyze `/data/anr/traces.txt` & Play Vitals stack traces; move all disk I/O (`SharedPreferences.apply()`/`commit()`, SQLite reads) off the main thread to **DataStore / Room on `Dispatchers.IO`**; avoid main-thread lock contention and heavy `BroadcastReceiver.onReceive()` work.
2. **Kotlin Coroutines**: *"Difference between `StateFlow` and `SharedFlow` for payment UI events?"*
   - **Your Answer**: `StateFlow` holds conflated current UI state (e.g., screen state), while `Channel(Channel.BUFFERED)` or `SharedFlow(replay = 0)` handles one-shot side effects (e.g., navigation or biometric prompt trigger) so configuration changes don't re-trigger a payment prompt.
3. **Multi-Module Architecture**: *"How do you structure a 100+ module Android codebase to keep incremental build times fast?"*
   - **Your Answer**: Separate `:api` (interfaces/models) and `:impl` (Hilt-bound implementations) modules per feature so changing `:feature:wealth:impl` never invalidates `:feature:payments:impl`.

---

## 4. Tailored STAR Stories (From Your Verified Career)
- **Guardian & Ayla Networks**: Highlight architecting hardware-backed encryption, resilient background state machines, and achieving **99.6%+ crash-free rate** across millions of device sessions.
- **Vectone Mobile ('Worktual')**: Highlight low-latency real-time state synchronization and custom UI performance.

---

## 5. Compensation & Closing Alignment
- **Submitted Figures**: Current Fixed `₹28.0 LPA` | Quoted Expected CTC: **`₹38.0 – 42.0 LPA`** (`16–30 days` notice period).
