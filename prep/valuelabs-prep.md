# Interview Preparation Guide — ValueLabs
**Role**: Lead Android Developer (Kotlin, Banking, AI, Jetpack Compose)
**LinkedIn Job ID**: `4469440664` | **Location**: Bengaluru, Karnataka

---

## 1. Role & Product Context
- **Focus**: Senior/Lead Android engineering for **Banking & Financial Services** digital products leveraging **Kotlin, Jetpack Compose, Android SDK, and AI-assisted mobile features**.
- **Submitted Highlights**: `12 years` total experience (`11 yrs` Android, `7 yrs` Kotlin, `10 yrs` Android SDK).

---

## 2. Banking Mobile System Design Scenario
### **Prompt**: *"Design a Secure Mobile Banking App with Biometric Login, Session Timeout, and AI Financial Insights."*
- **Key Architectural Pillars to Present**:
  1. **Zero-Trust Mobile Banking Security (MASVS-L2 / RBI Guidelines)**:
     - **Hardware-Backed Keystore + `BiometricPrompt.CryptoObject`**: Unlock an ECDSA/AES key stored in StrongBox/TEE only after biometric authentication succeeds.
     - **Certificate Pinning (`OkHttp CertificatePinner`) + Play Integrity API**: Block MITM proxies (Charles/Burp/Frida) and rooted/hooked devices.
     - **Inactivity Auto-Lock & App Switcher Privacy**: Lifecycle observer (`ProcessLifecycleOwner`) tracks background timestamps; enforce `WindowManager.LayoutParams.FLAG_SECURE` to blank out app switcher snapshots.
  2. **Jetpack Compose Banking Dashboard**:
     - Unidirectional Data Flow (`UiState`, `UiEvent`, `UiEffect`) with `StateFlow` and custom Canvas/Compose charts (`Circular SeekBar` experience!) for spending analytics.
  3. **AI Financial Assistant Integration**:
     - Streaming token responses over SSE (`Server-Sent Events`) into a Kotlin `Flow<String>`, rendering incremental markdown/cards in a `LazyColumn` with PII masking before network transmission.

---

## 3. High-Probability Technical Questions
1. **Security**: *"Why is simple boolean return from `BiometricPrompt.AuthenticationCallback` insecure for banking apps, and how does `CryptoObject` fix it?"*
   - **Your Answer**: A pure callback without `CryptoObject` can be bypassed via Frida method hooking. Passing a `Cipher` or `Signature` initialized with `setUserAuthenticationRequired(true)` forces the hardware Trusted Execution Environment (TEE) to cryptographically sign the challenge only when physical biometrics pass.
2. **Kotlin & Compose**: *"How do you handle complex form validation (NEFT/IMPS beneficiary transfer) in Jetpack Compose?"*
   - **Your Answer**: Hold field state + validation errors in an immutable `TransferFormState`, validate declaratively via `derivedStateOf` or ViewModel intent reducers, and preserve state across process death using `SavedStateHandle`.

---

## 4. Compensation Alignment
- **Target Compensation**: **`₹37.0 – 40.0 LPA`** (`+32%` hike on current `28 LPA` baseline, `30 days` notice period).
