# Bureau (Bureau.id) — Interview Preparation Guide

**Target Role**: Senior Android Engineer (Mobile Platform & Security SDK)  
**Location**: Bangalore, Karnataka, India (Hybrid)  
**Target Compensation**: ₹38.0 LPA (+35.7% hike on current 28 LPA baseline)  

---

## 1. Interview Loop Structure & Evaluation Rubric
1. **Recruiter Screen (30 mins)**: Career overview, security SDK engineering background, experience with Android OS internals and low-level Keystore primitives.
2. **Android Platform & Security Deep-Dive (60 mins)**: Staff Security Engineer — Android Keystore (StrongBox Keymaster), biometric authentication (`BiometricPrompt.CryptoObject`), Play Integrity API, anti-tampering/hooking defenses, and zero-trust mobile identity.
3. **SDK Architecture & Concurrency Coding (60 mins)**: Lead SDK Architect — Live Kotlin coding designing an embeddable, zero-dependency Android client SDK with minimal binary size (<500KB), non-blocking background initialization, and battery-friendly network batching.
4. **Behavioral & Engineering Values (45 mins)**: VP of Engineering — Security trade-offs vs. developer ergonomics, handling high-stakes client integrations, and collaborating with cross-functional backend risk teams.

---

## 2. Mobile System Design Blueprint: Embeddable Fraud Defense & Device Intelligence SDK
- **Problem**: Build a lightweight Android SDK that client apps (banking, e-commerce) embed to detect device tampering, emulator spoofing, and bot attacks in real time without degrading host app startup time or violating privacy policies.
- **Architectural Solution**:
  - **Zero-Dependency Core**: Pure Kotlin and standard Android framework APIs. No heavy third-party networking or serialization dependencies that could cause dependency version conflicts with the host app.
  - **Security Layer**:
    - Hardware-backed key generation via `KeyGenParameterSpec` with `setIsStrongBoxBacked(true)` fallback to standard TEE.
    - Device signature attestation combining Google Play Integrity API token with local cryptographic challenge-response nonces.
    - Runtime integrity detection: inspect `/proc/self/maps` for injected libraries (Frida, Xposed), verify package signing certificate digests, and check for root artifacts (`su` binaries, test-keys).
  - **Execution Engine**: Asynchronous non-blocking background collector using Kotlin Coroutines with an internal single-thread dispatcher. Expose clean, non-crashing public API interfaces (`Result<DeviceAttestation>`).

---

## 3. Deep-Dive Technical Q&A
- **Q1: How do you design an Android SDK so it never crashes or slows down the client host application?**
  - *Model Answer*: Wrap all public SDK entry points in defensive exception boundaries that swallow internal non-fatal errors and return structured `Result.failure` objects rather than throwing unchecked runtime exceptions. Enforce non-blocking architecture using background coroutine dispatchers so host app UI threads are never blocked. Keep binary footprint under 400KB by avoiding external libraries like Retrofit/Gson, relying on lightweight native `HttpURLConnection` and custom JSON parsing.
- **Q2: How do you prevent sensitive biometric authentication tokens from being intercepted in memory?**
  - *Model Answer*: Couple `BiometricPrompt` directly with a cryptographic cipher using `BiometricPrompt.CryptoObject(cipher)`. The hardware Keystore only unlocks the private key upon successful biometric verification inside the Secure World (TEE / StrongBox). The raw private key material is never exposed to the Android OS user space or RAM, neutralizing memory dumping attacks.
- **Q3: How does your work at Guardian and Ayla relate to Bureau's mission?**
  - *Model Answer*: At Guardian, I enforced enterprise-grade security across mobile clients, including hardware-backed Keystore biometric storage, OkHttp TLS 1.3 certificate pinning, and code obfuscation via Proguard/R8. At Ayla Networks, I built secure SDK layers connecting IoT devices and cloud endpoints with mutual TLS, encrypted token storage, and resilient edge reconciliation.

---

## 4. STAR Stories Mapped to Past Career
- **Situation (Guardian)**: Enterprise mobile app required banking-grade cryptographic security for sensitive user health and identity data.
- **Task**: Implement a resilient hardware-backed encryption and biometric authorization layer.
- **Action**: Architected a custom security module leveraging Android Keystore with StrongBox hardware backing, implemented `BiometricPrompt.CryptoObject` signing, and enforced TLS 1.3 certificate pinning with backup pin rotation.
- **Result**: Passed external third-party penetration testing with zero critical findings and 99.8% biometric authorization success rates across 50+ OEM device types.

---

## 5. Compensation Negotiation Script
> *"With 11+ years of software engineering expertise, verified experience building secure, high-concurrency mobile architectures at Guardian, Ayla Networks, and Vectone Mobile, and my specialized proficiency in Android Keystore, SDK design, and mobile security, my target compensation is **₹38.0 LPA** (+35.7% hike on current 28 LPA baseline)."*
