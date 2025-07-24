# Using a NavCam for Autonomous Lunar Position Determination
![NavCam Lunar Navigation](ArticleImage.jpg)
*Image credit: Richard Lourette and DALL-E*

**White Paper**

---

## Author’s Note

The motivation for writing this article came from a client request asking **how one would perform feature extraction for lunar imagery**. Since I have prior experience and insight into this topic, I decided to expand beyond just feature extraction and present the **bigger picture**, including alternate approaches and a detailed proposal for how a lunar spacecraft could use a navigation camera (NavCam) to determine its position in the lunar frame of reference.

---

## Executive Summary

As lunar missions expand in complexity, spacecraft must increasingly operate with autonomy. A spacecraft in lunar orbit, equipped with a star tracker, accurate orbital propagation, a high‑stability clock, and a navigation camera (NavCam), can use its NavCam imagery to determine its position in the lunar frame of reference without constant ground support.

This white paper outlines a detailed approach for using NavCam imagery combined with known lunar terrain models to estimate orbital position. It explains the purpose, benefits, and potential drawbacks of this method, and proposes an implementation pipeline. References are included so readers can explore technical topics in more depth.

---

## 1. Background and Motivation

### Why Autonomous Navigation?
- **Limited Earth contact:** During certain orbital phases or deep‑space operations, real‑time tracking from Earth is unavailable or delayed.
- **Precision requirements:** High‑accuracy positioning is critical for lander deployment, instrument pointing, and constellation coordination.
- **Operational resilience:** Reducing reliance on ground stations improves fault tolerance and mission efficiency.

### Subsystems on the Spacecraft
- **Star Tracker:** Provides precise spacecraft attitude (orientation) relative to celestial reference.
- **Orbital Telemetry & Propagator:** Predicts spacecraft state over time based on gravitational models and prior tracking.
- **Stable Clock:** ±10 ms accuracy supports accurate propagation and time‑tagging of measurements.
- **NavCam (Navigation Camera):** Downward‑looking imager capturing the lunar surface.

---

## 2. Concept: Terrain‑Relative Navigation Using NavCam

The idea is to compare **what the camera actually sees** to **what it should see** based on a known digital elevation model (DEM) of the Moon. Any differences translate into position corrections.

### Key Components
- **Lunar DEMs:** High‑resolution terrain models from missions like LRO/LOLA provide elevation and albedo data.  
  [NASA LOLA Data](https://lunar.gsfc.nasa.gov/lola.html)
- **Onboard Rendering:** Use current state estimate and Sun angle to render a synthetic view of terrain (ray‑traced).
- **Image Registration:** Align the NavCam image with the rendered image using robust techniques (phase correlation, feature matching).

---

## 3. Technical Approach

### 3.1 Image Capture and Preprocessing
- NavCam captures an image of the surface.
- Preprocess to normalize illumination:
  - Apply **CLAHE (Contrast Limited Adaptive Histogram Equalization)** to balance brightness.  
    [CLAHE explanation](https://en.wikipedia.org/wiki/Adaptive_histogram_equalization)
  - Alternatively, compute **edge or gradient maps** to reduce sensitivity to shadows.

### 3.2 Generate Predicted View
- From current position estimate and known Sun vector:
  - Perform **ray tracing** into DEM to create a synthetic image that matches camera intrinsics.
  - Include reflectance models (Lambertian or Hapke) for realistic shading.
- This predicted image represents what the camera should see if the position estimate were perfect.

### 3.3 Register Images
- Use **phase correlation** in the frequency domain to find translation between predicted and actual images:
  - FFT both images, compute cross‑power spectrum, inverse FFT → yields shift in pixels.
  - For large uncertainties, use hierarchical or log‑polar methods to also handle rotation/scale.  
    [Phase Correlation overview](https://en.wikipedia.org/wiki/Phase_correlation)

**Alternatively or additionally:**
- Extract robust features from both images and match using descriptors:
  - **ORB (Oriented FAST and Rotated BRIEF):** Efficient, binary descriptors well‑suited for embedded systems.  
    [ORB Feature Detector](https://docs.opencv.org/4.x/db/d95/classcv_1_1ORB.html)
  - **BRISK (Binary Robust Invariant Scalable Keypoints):** Scale‑ and rotation‑invariant, computationally efficient, and illumination‑robust; a strong alternative to SIFT/SURF for resource‑constrained systems.  
    [BRISK Overview](https://ieeexplore.ieee.org/document/6126544)

### 3.4 Convert Image Shift to Ground Offset
- Pixel offsets translate to ground offsets based on altitude and camera intrinsics:  
\[
\Delta X = \frac{\Delta u}{f} \cdot h,\quad \Delta Y = \frac{\Delta v}{f} \cdot h
\]
where \(f\) = focal length in pixels, \(h\) = altitude.

- Transform offset from camera frame to lunar frame using attitude matrix.

### 3.5 Fuse with Propagation (EKF)
- Feed position correction into an **Extended Kalman Filter (EKF)** alongside orbital dynamics model.  
  [Kalman Filter Basics](https://en.wikipedia.org/wiki/Kalman_filter)
- EKF updates the spacecraft state (position and velocity) and uncertainty.

---

## 4. Pros and Cons

### ✅ Benefits
- **Illumination‑robust:** By rendering with current Sun angles or using edge‑based matching.
- **High accuracy:** With high‑res DEMs, meter‑level positioning is achievable.
- **No heavy ground infrastructure:** Independence from Earth‑based tracking.
- **Reusable:** Same method can support landing, formation flight, or low‑orbit operations.

### ⚠️ Drawbacks
- **Compute load:** Real‑time rendering and registration require significant onboard processing (GPU or FPGA may be needed).
- **Data storage:** Storing DEM tiles and albedo maps needs careful memory management.
- **DEM accuracy limits:** Position accuracy is bounded by the resolution and accuracy of the terrain model.
- **Complex implementation:** Requires careful integration of attitude knowledge, camera calibration, and image processing pipelines.

---

## 5. Recommended Implementation Pipeline

1. **Acquire NavCam frame** with star‑tracker attitude.
2. **Preprocess image** (edge map or CLAHE).
3. **Render synthetic view** from DEM and estimated position.
4. **Perform registration** (phase correlation or feature matching with ORB/BRISK).
5. **Compute pixel offset → ground offset.**
6. **Fuse offset with propagation in EKF** to update position.
7. Repeat at regular intervals or when orbital drift exceeds threshold.

---

## 6. References & Further Reading

- NASA LOLA Data for Lunar DEMs: [https://lunar.gsfc.nasa.gov/lola.html](https://lunar.gsfc.nasa.gov/lola.html)  
- LROC Imagery Resources: [https://lroc.sese.asu.edu/](https://lroc.sese.asu.edu/)  
- Phase Correlation Techniques: [https://en.wikipedia.org/wiki/Phase_correlation](https://en.wikipedia.org/wiki/Phase_correlation)  
- Extended Kalman Filters Overview: [https://en.wikipedia.org/wiki/Kalman_filter](https://en.wikipedia.org/wiki/Kalman_filter)  
- ORB Detector: [https://docs.opencv.org/4.x/db/d95/classcv_1_1ORB.html](https://docs.opencv.org/4.x/db/d95/classcv_1_1ORB.html)  
- BRISK Paper: [https://ieeexplore.ieee.org/document/6126544](https://ieeexplore.ieee.org/document/6126544)

---

## 7. Conclusion

The approach outlined above offers a practical and robust way for a lunar spacecraft to autonomously determine its position in the lunar frame of reference. By leveraging NavCam imagery, high‑fidelity lunar terrain models, and well‑established image registration techniques like phase correlation or feature‑based matching (ORB, BRISK), the spacecraft can achieve high accuracy without reliance on Earth‑based navigation aids.

While this method introduces computational and integration challenges, the benefits in operational autonomy and positioning precision make it a compelling solution for advanced lunar missions.

---

**Prepared as a technical response to the client’s request.**
