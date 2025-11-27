# Using a Navigation Camera to Achieve Meter-Level Position Knowledge on the Moon (Without GNSS or Earth Tracking)  
**A practical, flight-proven approach that is already flying on half the Artemis-era landers**

# Using a NavCam for Autonomous Lunar Position Determination
![NavCam Lunar Navigation](ArticleImage.jpg)
*Image credit: Richard Lourette and DALL-E*

**Richard W. Lourette**  
RL Tech Solutions LLC  
November 2025  

### TL;DR  
If your spacecraft can see the ground and you have a good map, you don’t need GPS or constant Earth tracking to know where you are. You can achieve 1–3 meter accuracy anywhere on the Moon, far side included.  
Here’s exactly how it works in 2025.

### 1. The Problem Everyone Talks About  
Classic lunar orbit determination relies on Earth-based radiometric tracking. It delivers 10–100 m accuracy with hours between updates and zero coverage on the far side.  
Future LunaNet/Moonlight GNSS works great when signals are visible, but huge gaps remain in polar craters and on the far side.

### 2. The Simple, Elegant Fix That Actually Works  
Take a picture of the ground, render what that picture should look like from your current best-guess position using an onboard lunar map, measure the difference, and correct your position.  
Repeat every 30–120 seconds.

This technique is called Terrain-Relative Navigation (TRN) using a NavCam. It already flies on Astrobotic Griffin, Firefly Blue Ghost, Intuitive Machines Nova-C/D, ispace Resilience, JAXA SLIM follow-ons, and most CLPS missions.

### 3. What You Actually Need Onboard (all COTS or near-COTS in 2025)

| Item                  | Typical Spec (2025 flight hardware)          | Why it matters                              |
|-----------------------|---------------------------------------------|---------------------------------------------|
| NavCam                | 1–4 Mpixel, 12-bit, 10–30° FOV              | Sees craters & rocks                        |
| Laser altimeter       | 5–20 Hz, ±5–20 cm range                     | Turns pixels into real meters               |
| Star tracker          | ≤10 arcsec attitude                         | Provides precise pointing knowledge         |
| Good clock            | ±10 ms absolute                             | Enables accurate time-tagging               |
| Lunar map             | SLDEM2020 or LOLA+Kaguya merged, 5–10 m grid| Serves as the Moon’s “GPS map”              |

### 4. How It Works: Step by Step (the 6 steps that matter)

1. Propagate your orbit using high-fidelity lunar gravity (GRAIL-based) and solar radiation pressure (standard practice).  
2. Trigger a perfectly timed NavCam frame, laser range, and star-tracker attitude at the same millisecond.  
3. Ray-trace the onboard DEM from your current estimated position using the exact Sun vector and a realistic surface-brightness model such as [Hapke](https://en.wikipedia.org/wiki/Hapke_parameters) or [Lommel-Seeliger](https://en.wikipedia.org/wiki/Lommel%E2%80%93Seeliger_law). These models predict how bright each patch of lunar soil (its [albedo](https://en.wikipedia.org/wiki/Albedo)) should appear under the current lighting angle, including accurate shadows cast by craters and rocks. Matching illumination and shadows is the secret sauce that makes registration rock-solid even over bland terrain.  
4. Register real versus synthetic image using phase correlation in the Fourier domain (fast and extremely robust) or modern alternatives such as ECC or neural matchers.  
   → Phase correlation: https://en.wikipedia.org/wiki/Phase_correlation  
   → Enhanced Correlation Coefficient (ECC): https://learnopencv.com/image-alignment-ecc-in-opencv-c-python/  
5. Convert sub-pixel shift × laser range × camera geometry into meters of position error on the ground.  
6. Feed that measurement into an [Extended Kalman Filter (EKF)](https://en.wikipedia.org/wiki/Extended_Kalman_filter) or a [factor-graph navigator (iSAM2)](https://gtsam.org/) for an instantly corrected orbit.

Total cycle time on a modern space processor: 300–600 ms, which yields 1–3 Hz updates.

### 5. Real-World Accuracy (2025 numbers, not slides)

| Altitude | DEM used                | Typical registration | Total 1σ horizontal |
|----------|-------------------------|----------------------|---------------------|
| 100 km   | 10 m global             | 0.15 pixel           | 3–5 m               |
| 50 km    | 10 m global             | 0.12 pixel           | 1–3 m               |
| 20–30 km | 5 m polar               | 0.10 pixel           | 0.7–1.5 m           |
| <10 km   | 1–2 m LROC NAC mosaics  | 0.08 pixel           | <50 cm              |

These figures come from NASA, JAXA, and commercial flight data (SLIM, Chang’e-5/6, and ongoing CLPS testing).

### 6. Bonus: Makes Future Lunar GNSS Even Better  
When LunaNet or Moonlight signals become available, TRN bridges the gaps and drastically reduces the number of satellites required for continuous meter-level navigation.

### 7. Why This Changes Everything for Commercial Lunar Missions  
- No more paying \$5k–\$10k per DSN pass  
- Far-side missions finally receive real navigation  
- Small-sat constellations can maintain 10–50 m spacing autonomously  
- Precision landing becomes almost trivial because you already know exactly where you are before the descent burn starts

### 8. Real-World Challenges (yes, they exist — and they’re solvable)

| Challenge                          | Current 2025 Reality                                                                 | How missions actually handle it today                                      |
|------------------------------------|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Onboard compute budget             | Ray-tracing + registration needs ~200–400 ms on a modern space CPU/GPU               | Tiled DEMs, GPU/FPGA acceleration, run at 0.5–2 Hz (more than enough)      |
| DEM gaps or lower resolution       | Some equatorial regions still ~30 m/post; shadowed polar craters have sparse data   | Pre-load high-res LROC NAC mosaics for landing zones; accept 3–5 m in cruise |
| Very low-contrast terrain          | Flat mare at high Sun angle can look almost featureless                             | Fall back to edge maps or schedule images at lower Sun angles               |
| Memory for global high-res map     | Full 5 m global DEM + albedo ≈ 1.2 GB uncompressed                                   | Tile + compress; most missions only load polar + landing corridor (~300 MB)|
| Radiation-induced bit flips        | Lunar orbit is harsh                                                                 | ECC memory + tile checksums; re-upload corrupted tiles from Earth when needed |

None of these are show-stoppers — every CLPS and Artemis lander flying TRN in 2025–2027 has already solved them with today’s flight hardware.

### 9. Bottom Line  
If you are building anything that flies around or lands on the Moon in the next five years and you are not using NavCam TRN, you are spending extra money and taking extra risk.

It really is the closest thing the Moon has to GPS, and it works today.

Want to discuss architecture, flight software, DEM tiling, camera selection, or next-generation fusion of vision TRN with lunar (or terrestrial) GNSS? Drop me a message.

– Richard  
📧 Contact: rlourette[at]gmail[dot]com
🌐 Location: Fairport, New York, USA 

### About the Author  
Richard W. Lourette is the founder of RL Tech Solutions LLC and a veteran navigation and payload engineer with more than 20 years delivering high-precision positioning systems for industry leaders such as Topcon Positioning, L3Harris, and Panasonic. He holds 20 U.S. patents.

Richard is especially passionate about two converging frontiers:  
1. Vision-based Terrain-Relative Navigation for the Moon, asteroids, and Mars  
2. Terrain-aided and vision-aided augmentation of terrestrial GNSS in urban canyons, forests, and contested environments

He is actively seeking partnerships and contracts that fuse high-performance imaging systems with GNSS and alternative PNT to create next-generation resilient navigation for space, aviation, and autonomous vehicles.

If your team is working on lunar navigation, precision landing, cislunar GNSS augmentation, or terrain-augmented GNSS on Earth, let’s talk. Richard is looking for the next challenge where these worlds collide.