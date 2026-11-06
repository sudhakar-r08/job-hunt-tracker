# Dexcom — Interview Preparation Guide

**Target Role**: Staff SW Development Engineer (Mobile & IoT Platform)  
**Location**: Bengaluru, Karnataka, India (Hybrid)  
**Target Compensation**: ₹41.0 LPA (+46.4% hike on current 28 LPA baseline, well positioned within Dexcom Staff band in Bengaluru)  

---

## 1. Interview Loop Structure & Evaluation Rubric
1. **Recruiter Screen (30 mins)**: Career background, deep dive into past BLE and connected IoT experience (Ayla Networks, Infitech), comfort with Bengaluru hybrid model, notice period (90 days, negotiable), and target compensation (₹41.0 LPA).
2. **Technical Deep-Dive: BLE State Machines & Concurrency (60 mins)**: Staff / Principal Mobile Architect — Deep dive into Android Bluetooth Low Energy (BLE) peripheral communication, serialized GATT command dispatchers, resolving error 133, connection interval parameters, MTU negotiation, and Kotlin Coroutines/Flow concurrency.
3. **Medical IoT Mobile System Design (60 mins)**: Engineering Director / Medical Device Systems Architect — Design a continuous glucose monitoring (CGM) companion app streaming sensor values every 5 minutes 24/7 over BLE, generating high/low urgent glucose alerts during Doze mode, buffering readings offline for up to 30 days, and synchronizing with Dexcom Cloud with zero data loss.
4. **Hands-On Live Coding & Algorithms (60 mins)**: Senior Staff Engineer — CoderPad/HackerRank coding in Kotlin/Java. Concurrency primitives, thread-safe ring buffers, time-series aggregation, and unit test coverage.
5. **Behavioral, Leadership & Medical Compliance (45 mins)**: Engineering Manager — Mentoring engineers, driving technical design RFCs, cross-functional collaboration with firmware and regulatory compliance teams, and handling high-stakes medical device reliability.

---

## 2. Mobile System Design Blueprint: Dexcom Continuous Glucose Monitoring (CGM) Engine
- **Problem Statement**: Architect the core Android client engine for Dexcom's continuous glucose monitoring system. A wearable sensor transmitter communicates via BLE with an Android phone. The app must maintain a dependable 24/7 background connection, receive sensor readings every 5 minutes, trigger life-saving audible alarms for hypoglycemic events even when the phone is on "Do Not Disturb" (DND) or in deep Doze mode, and sync telemetry securely to Dexcom Share/Follow cloud services.
- **Architectural Solution**:
  - **BLE Hardware Abstraction (`:core:ble`)**:
    - Wraps `BluetoothGatt` inside a serialized finite state machine (`DISCONNECTED` ➔ `CONNECTING` ➔ `CONNECTED` ➔ `SERVICES_DISCOVERED` ➔ `SUBSCRIBED` ➔ `STREAMING`).
    - Enforces a dedicated single-thread dispatcher (`newSingleThreadContext("DexcomBleDispatcher")`) to serialize all GATT operations sequentially, completely avoiding Android GATT status 133 collisions.
    - Configures connection priority (`CONNECTION_PRIORITY_BALANCED` during standard telemetry, `CONNECTION_PRIORITY_HIGH` during pairing or firmware update).
  - **Foreground Service & Urgent Alarm Dispatcher (`:core:alarm`)**:
    - High-priority foreground service with persistent notification (`startForeground()`) ensures Android OS never terminates the telemetry collector process.
    - Utilizes `AlarmManager.setExactAndAllowWhileIdle()` to wake the CPU during Doze mode for time-critical glucose checks.
    - Leverages Android `NotificationChannel` with `NotificationManager.IMPORTANCE_HIGH` and `setBypassDnd(true)` to trigger loud audio alerts during life-threatening low-glucose events (<55 mg/dL).
  - **Encrypted Time-Series Persistence (`:core:database`)**:
    - Glucose readings are persisted into an encrypted **Room DB** table (AES-256 via SQLCipher).
    - Monotonically increasing sequence numbers guarantee detection of missing data packets, triggering automated historical backfill requests from the transmitter.
  - **Cloud Synchronization (`:core:sync`)**:
    - Dispatches encrypted batches of glucose telemetry to Dexcom Cloud via HTTPS/TLS 1.3 with OkHttp certificate pinning.

---

## 3. Deep-Dive Technical Q&A

- **Q1: Android's BLE stack is notorious for the random status 133 error during GATT connection. What are the root causes and how do you prevent them in a critical medical device app?**
  - *Model Answer*: 
    1. **Resource Exhaustion & Stale Handles**: Status 133 typically occurs when previous `BluetoothGatt` instances were not explicitly closed. We must always call `gatt.disconnect()` followed immediately by `gatt.close()` upon disconnection or failure to release the native hardware handle.
    2. **Command Overlap**: The Android BLE stack cannot queue concurrent GATT operations natively. If `discoverServices()` is called before `onConnectionStateChange()` completes, error 133 occurs. We serialize every single GATT operation onto a sequential single-threaded worker queue.
    3. **Exponential Backoff Reconnect**: We avoid hammering the Bluetooth adapter with immediate reconnection loops. When error 133 triggers, we wait with an exponential backoff (1s, 2s, 4s, up to 30s) and random jitter, listening for system `BluetoothAdapter.ACTION_STATE_CHANGED` broadcasts.

- **Q2: In Android 12+, how do you handle background execution and Bluetooth scanning without draining the battery or getting killed by Doze mode?**
  - *Model Answer*: 
    1. **Foreground Service**: We declare a foreground service with `android:foregroundServiceType="connectedDevice|dataSync"`, maintaining an ongoing sticky notification that exempts the process from low-memory killer (LMK) termination.
    2. **Targeted Direct Connection**: Rather than running battery-draining continuous BLE discovery scans (`BluetoothLeScanner`), we use `bluetoothDevice.connectGatt(context, false, gattCallback)` directly targeting the paired sensor's known MAC address.
    3. **Exemption from Battery Optimization**: We request `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` for life-critical medical devices so the OS does not throttle network sockets or defer alarms during deep sleep.

- **Q3: How do you verify and maintain 100% data integrity when a patient travels without phone connectivity for several days?**
  - *Model Answer*: 
    1. **Transmitter Buffering & Sequence IDs**: The Dexcom sensor hardware transmitter buffers readings locally with unique sequence IDs.
    2. **Client-Side Gap Detection**: Upon BLE reconnection, the mobile client reads the transmitter's current sequence ID. If a gap exists between the last stored sequence in `Room DB` and the current ID, the app initiates a historical backfill command to pull missed packets.
    3. **Idempotent Storage & Cloud Sync**: Data points are inserted into `Room DB` with `OnConflictStrategy.IGNORE` using the sequence ID as primary key. Cloud sync dispatches batches using an `idempotency_key`, preventing duplicate readings on backend patient charts.

- **Q4: How does your background at Ayla Networks and Guardian directly position you to lead this role at Dexcom?**
  - *Model Answer*: At Ayla Networks, I led mobile development for connected IoT platforms. I engineered resilient BLE device provisioning state machines with automatic retry backoff that slashed pairing failures by 25%, and built offline data synchronization with Room DB. At Guardian, I serve as Lead Mobile Engineer / Architect, establishing Clean Architecture and 99.85%+ crash-free session rates for enterprise applications. Dexcom’s core challenge—maintaining bulletproof 24/7 BLE connectivity, real-time vital telemetry, and zero data loss—is identical to the systems I scaled in production at Ayla Networks.

---

## 4. STAR Stories Mapped to Past Career

### Story 1: Overhauling BLE Hardware Provisioning & Eliminating Dropouts (Ayla Networks)
- **Situation**: Connected IoT edge devices experienced frequent pairing drops and timeout errors during customer onboarding due to OEM BLE stack variations across Android devices.
- **Task**: Re-architect the device provisioning and BLE pairing flow to guarantee reliable connection across all supported Android versions and device manufacturers.
- **Action**: Built an explicit finite state machine (FSM) enforcing serialized GATT command execution; implemented dynamic MTU negotiation; added proactive connection cleanup (`gatt.close()`) upon failure; and created an automated fallback mechanism.
- **Result**: Reduced device onboarding dropouts by 25%, halved connection pairing time from 45s to 18s, and raised Play Store rating from 3.8 to 4.5.

### Story 2: Resilient Offline-First Data Caching & Zero Telemetry Loss (Ayla Networks)
- **Situation**: Field IoT controllers operated in intermittent cellular/Wi-Fi environments, risking telemetry data drops.
- **Task**: Architect an offline-first transaction and state synchronization pipeline.
- **Action**: Designed a persistent offline caching layer using Room DB with transactional event dispatch queues and exponential backoff retry policies; synchronized state over persistent WebSockets with automated reconnection.
- **Result**: Achieved 100% data delivery with zero telemetry loss during network drops.

### Story 3: Enterprise Quality Governance & Stability Overhaul (Guardian)
- **Situation**: Enterprise mobile codebases were tightly coupled, resulting in slow feature delivery and regression risks during releases.
- **Task**: Establish architectural guidelines, Clean Architecture modularization, and strict quality gates across distributed feature teams.
- **Action**: Led the decomposition into decoupled multi-modules with clear visibility boundaries; introduced automated CI/CD linting, static analysis, and code coverage thresholds (>80%); and instituted an engineering RFC review culture.
- **Result**: Reduced clean build times by 35%, lowered crash rates to achieve 99.85%+ crash-free sessions, and successfully onboarded 15+ engineers to standardized architectural practices.

---

## 5. Compensation Negotiation Script
> *"With 11+ years of software engineering expertise, verified track record leading IoT connected device and mobile architecture at Guardian and Ayla Networks, and my specialized hands-on ability to solve complex BLE hardware communication, low-latency telemetry, and zero-data-loss mobile architectures, my target compensation is **₹41.0 LPA** (+46.4% hike on current 28 LPA baseline, well aligned with Dexcom's Staff Software Engineer band in Bengaluru)."*
