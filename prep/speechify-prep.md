# Speechify — Interview Preparation Guide

**Target Role**: Team Lead, Android Core Product (Audio & AI)  
**Location**: Bangalore, India (Remote / Hybrid)  
**Target Compensation**: ₹38.0–42.0 LPA (+35% to +50% hike on current 28 LPA baseline)  

---

## 1. Interview Loop Structure & Evaluation Rubric
1. **Recruiter Screen (30 mins)**: High-level technical leadership background, experience with consumer Android apps scaling to millions of users, and alignment with Speechify’s mission.
2. **Android Architecture & System Design (60 mins)**: Architect a low-latency text-to-speech audio streaming and document synchronization engine (handling continuous audio playback, on-the-fly voice synthesis, sentence highlighting, and cross-device sync).
3. **Hands-On Coding & Concurrency (60 mins)**: Live Kotlin / Coroutines coding session focused on thread-safe buffer queues, custom reactive operators, and memory management for large file parsing (PDF/ePub/OCR).
4. **Engineering Leadership & Founder Alignment (45 mins)**: Team mentoring, code quality culture, handling ambiguous product specs, and high-velocity shipping mindset.

---

## 2. Mobile System Design Blueprint: Real-Time Audio Streaming & Word Highlighting Engine
- **Problem**: Stream AI synthesized audio packets continuously while dynamically highlighting the active word/sentence in a 500-page book without UI frame stutters or audio buffer underruns.
- **Architectural Solution**:
  - **Media Player Layer**: Android `Media3 / ExoPlayer` embedded in a dedicated foreground `MediaSessionService` to prevent OS background killing during screen-off playback.
  - **Synchronization Engine**: Pre-compute sentence timestamp alignment markers (`WordTimingChunk(startMs, endMs, tokenRange)`) delivered alongside audio buffers. Use a `SharedFlow` conflated stream to decouple the 60Hz UI text-highlighting animator from the 44.1kHz audio hardware clock.
  - **Memory & Parsing Strategy**: Memory-mapped files (`MappedByteBuffer`) for multi-megabyte PDF/ePub documents to avoid Out-Of-Memory (OOM) heap spikes during parsing.
  - **Offline Caching**: LRU disk cache for downloaded AI audio chunks backed by Room DB metadata, enabling seamless offline listening and auto-purge of old audio files.

---

## 3. Deep-Dive Technical Q&A
- **Q1: How do you prevent audio glitches and stuttering during background playback on Android?**
  - *Model Answer*: Run audio decoding and playback logic inside a foreground `MediaSessionService` with a high-priority ongoing notification. Use a dedicated background thread dispatcher (`Dispatchers.IO` for file I/O and a single-thread custom dispatcher for audio buffer queueing) to prevent thread starvation from CPU-heavy UI operations. Ensure buffer headroom is maintained at 3–5 seconds ahead of current playback.
- **Q2: How do you achieve 60fps / 120fps smooth recomposition in Jetpack Compose when reading continuous fast-moving streams?**
  - *Model Answer*: Never pass raw fast-changing timestamp primitives (`currentTimeMs`) directly to high-level composables. Use `@Stable` and `@Immutable` data wrappers and derive state using `derivedStateOf` so only the specific active word chip recomposes while the surrounding paragraph text remains untouched. Leverage `rememberUpdatedState` and `Modifier.drawWithContent` for custom cursor animations to bypass layout and measure phases completely.
- **Q3: How did your experience at Vectone and Infitech prepare you for audio/media streaming at Speechify?**
  - *Model Answer*: At Vectone Mobile, I led the native Android architecture for the Worktual UCaaS platform, solving real-time WebRTC audio packet loss, jitter buffer management, and audio focus ducking across diverse Android OEM devices. At Infitech Reality, I built edge computer vision and audio pipelines, managing memory-constrained native libraries (C++ NDK / OpenCV) without memory leaks.

---

## 4. STAR Stories Mapped to Past Career
- **Situation (Vectone Mobile)**: Real-time audio and VoIP calls suffered from packet jitter and audio focus conflicts when background notifications arrived.
- **Task**: Overhaul audio lifecycle management and eliminate frame lag during active calls.
- **Action**: Implemented an automated `AudioFocusRequestCompat` state machine, segregated audio buffer processing onto a dedicated high-priority native thread, and built custom reactive state operators in Coroutines to handle network switches smoothly.
- **Result**: Reduced call audio drop rates by 42% and achieved 99.6% crash-free sessions across 100K+ mobile users.

---

## 5. Compensation Negotiation Script
> *"Given my 11+ years of software engineering expertise, verified track record leading real-time media and communications architecture at Guardian, Ayla Networks, and Vectone Mobile, and my readiness to drive the core Android audio engine at Speechify, my target compensation is **₹40.0 LPA** (all-cash or top-tier equity hybrid, representing a +42.8% hike on my current 28 LPA baseline)."*
