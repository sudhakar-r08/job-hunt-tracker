# Interview Preparation Guide — YouTrip
**Role**: Staff Mobile Engineer (Architecture & Performance)
**LinkedIn Job ID**: `4476570656` | **Location**: Bengaluru, Karnataka (Hybrid)

---

## 1. Role & Product Context
- **Product**: **YouTrip** is Southeast Asia's leading multi-currency digital wallet and cross-border commercial card platform (`150+ currencies`, real-time FX exchange, virtual/physical Mastercard issuance).
- **Why You Were Shortlisted**: Your application explicitly matched their need for a **Staff Mobile Engineer** spanning **Native Android (Kotlin, Jetpack Compose, NDK)** AND **Cross-Platform (Flutter, Kotlin Multiplatform - KMP)** with strong mobile security and fintech reliability.

---

## 2. Mobile System Design Scenario
### **Prompt**: *"Design a Real-Time Multi-Currency FX Exchange & Virtual Card Provisioning Module shared across Android & iOS."*
- **Key Architectural Pillars to Present**:
  1. **Shared Domain & Data Layer (KMP or Flutter Module)**:
     - Share deterministic decimal FX rate calculations (`BigDecimal` / integer minor-unit representation—never `Double`/`Float` for money!), quote expiration countdown timers, and API retry policies across Android & iOS.
  2. **Live FX Quote Streaming**:
     - Stream live FX rates via WebSocket / gRPC-Web with a 15-second locked quote token (`quote_id` + `expires_at`) when the user taps "Exchange".
  3. **MAS / PCI-DSS Mobile Security**:
     - Biometric step-up authentication (`BiometricPrompt` with `CryptoObject` signature), screen-capture prevention (`FLAG_SECURE`) on PAN/CVV screens, root/jailbreak/frida detection, and NDK/C++ obfuscation for sensitive keys.

---

## 3. High-Probability Staff-Level Questions
1. **Staff Engineering Leadership**: *"How do you drive architectural RFCs and align Android, iOS, and Backend teams?"*
   - **Your Answer**: Share how at **Guardian** and **Ayla Networks** you authored mobile architecture RFCs, defined OpenAPI/Protobuf contracts upfront with backend teams, established automated CI lint/detekt gates, and mentored senior engineers.
2. **Cross-Platform Tradeoffs (Kotlin Multiplatform vs. Flutter vs. Native)**:
   - **Your Answer**: Use **KMP** when sharing complex business logic, networking (`Ktor`), and local storage (`SQLDelight`/`Room`) while keeping 100% native Jetpack Compose / SwiftUI UIs; use **Flutter** when unified custom-rendered UI across both platforms accelerates feature velocity.
3. **Precision & Concurrency in Fintech UI**:
   - **Your Answer**: Always represent currency in minor units (`Long` cents/paise) + ISO-4217 currency code; use debounced `flatMapLatest` in Kotlin `Flow` when the user types an amount so stale FX quotes never overwrite newer quotes.

---

## 4. Compensation & Closing Alignment
- **Submitted Figures**: Current Base `₹28.0 LPA` | Quoted Expected Base: **`₹38.0 LPA`** (`4 weeks` notice period).
