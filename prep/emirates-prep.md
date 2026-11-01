# Interview Preparation Guide — Emirates Group
**Role**: Senior Technical Software Engineer (Mobile & Edge AI / Computer Vision — Req `#25824`)
**Location**: Dubai, United Arab Emirates (UAE) | **Portal**: `emiratesgroupcareers.com`

---

## 1. Role & Product Context
- **Product**: Emirates Group's next-generation digital travel, biometric smart-gate/airport operations, and consumer mobile ecosystems in Dubai.
- **Key Focus Areas**: High-reliability mobile & edge software engineering, on-device computer vision / camera pipelines (CameraX, ML Kit, TensorFlow Lite / ONNX Runtime), real-time telemetry, and enterprise-scale architecture.

---

## 2. Mobile & Edge AI System Design Scenario
### **Prompt**: *"Design an On-Device Passport/Boarding-Pass & Biometric Verification Module for the Emirates Mobile App & Airport Kiosks."*
- **Key Architectural Pillars to Present**:
  1. **Zero-Copy Camera Pipeline (`CameraX` + `ImageAnalysis` + NDK/GPU Delegate)**:
     - Process camera frames at 30 FPS on a dedicated background executor using `STRATEGY_KEEP_ONLY_LATEST` backpressure so the UI thread never drops frames.
  2. **On-Device Edge Inference + NFC ePassport Read**:
     - Run document boundary detection & OCR on-device (TFLite / ML Kit) followed by **NFC ISO-14443 BAC/PACE chip reading** for cryptographic passport verification—working even when airport connectivity fluctuates.
  3. **Privacy & Security by Design**:
     - Ephemeral in-memory frame buffers (zero disk persistence of raw biometric frames), TLS 1.3 mutual authentication (`mTLS`) to Emirates identity services.

---

## 3. High-Probability Technical & Leadership Questions
1. **Hardware & IoT / Edge Integration (Your Core Strength from Guardian & Ayla Networks)**:
   - *"Tell us about your experience integrating mobile apps with hardware sensors, BLE/Wi-Fi, or edge processing."*
   - **Your Answer**: Walk through your architecture at **Guardian** and **Ayla Networks**, where you led mobile + IoT SDK engineering for BLE/Wi-Fi provisioning, real-time device telemetry, and native Android performance tuning across millions of connected endpoints.
2. **Memory & Thermal Management on Mobile**:
   - *"How do you prevent OutOfMemoryError (OOM) and thermal throttling during continuous camera/media processing?"*
   - **Your Answer**: Reuse `Bitmap` pools / `ImageProxy.close()` deterministically in `finally` blocks, downsample resolution to model input tensor size before inference, and monitor `PowerManager.OnThermalStatusChangedListener`.

---

## 4. UAE Relocation & Compensation Alignment
- **Target Compensation**: **`AED 30,000 – 34,000 / month` tax-free** (~`₹80–90 LPA` equivalent) + Emirates Group flight/medical/relocation benefits in Dubai.
- **Notice Period**: `30 days` (Indian Passport ready for immediate UAE employment visa sponsorship).
