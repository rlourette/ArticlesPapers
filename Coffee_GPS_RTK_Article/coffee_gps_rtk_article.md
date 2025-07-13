
# How My Morning Coffee Reveals the Magic of GPS RTK Technology

*By Richard Lourette · Published May 23, 2025*

![Yarbo mowing with GPS RTK](rtk%20article.jpg)


Picture this: I'm sitting by my firepit at 6 AM, steam rising from my coffee cup, the morning dew still glistening on the grass. Behind me, my Yarbo robot is already hard at work, methodically mowing perfect stripes across my 3‑acre lawn. No boundary wires. No supervision needed. Just centimeter‑level precision powered by the same GPS technology I spent over a decade helping develop.

As someone who worked on the GPS III satellite payload at L3Harris for over 10 years (from pre‑proposal through production), and recently contributed to Topcon Positioning System's new HiPer XR GPS receiver, watching this autonomous robot navigate my property feels like witnessing the culmination of decades of innovation.

---

## The RTK Revolution: From "Close Enough" to "Dead On"

Traditional GPS (like in your smartphone) gets you within about 3–10 meters of your actual location. That’s fine for finding your local coffee shop, but imagine if your lawn mower had that accuracy—you’d get some very creative landscaping!

**Enter Real‑Time Kinematic (RTK) GPS.** It transforms that 3 m uncertainty into jaw‑dropping 1 cm precision. How? By using corrections and clever mathematics.

---

## The Secret Sauce: Base Stations and Real‑Time Corrections

My Yarbo doesn’t just listen to satellites—it maintains a constant conversation with a base station mounted on my home that knows **exactly** where it is. This Yarbo Data Center continuously averages its position over time to establish its precise coordinates down to millimeters.

Both the base station and my robot calculate their positions multiple times per second. Since the base station is stationary, any variation in its calculated position indicates an error—caused by atmospheric disturbances, satellite clock errors, etc. It sends real‑time corrections to Yarbo using Wi‑Fi HaLow, a long‑range wireless protocol operating in the sub‑1 GHz spectrum (penetrates obstacles and can reach over a kilometer).

---

## The Brain Behind the Precision: Kalman Filters at Work

Yarbo doesn’t simply apply the corrections—it uses **Kalman filters** (named after Rudolf Kálmán), sophisticated mathematical algorithms that:

1. **Predict** where the robot should be based on movement and previous state  
2. **Compare** that prediction to the GPS‑measured position  
3. **Fuse** the data, optimally weighting measurements and predictions  

This results in incredibly smooth, accurate, centimeter‑level navigation.

---

## Why It Feels Like Magic (Actually, Science)

- 📍 **Centimeter‑level accuracy** over acres—no wires, no manual guidance  
- 🔄 **Real‑time corrections** ensure the robot navigates in harmony with the base station  
- 🧠 **Kalman filtering** blends sensor data intelligently, compensating for noise and uncertainty  

---

## TL;DR

- Standard GPS = ~3–10 m accuracy  
- RTK GPS (with base station + corrections) = ~1 cm accuracy  
- Kalman filters = 💡 “data fusion magic” enabling ultra‑precise navigation  
