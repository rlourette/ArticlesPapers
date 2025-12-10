# Ubiquitous Location: Extending P1's Platform from Outdoor GNSS to Indoor and Asset-Level Visibility

<p align="center">
  <img src="Ubiquitous_Location-Extending_P1s_Platform_from_Outdoor_GNSS_to_Indoor_and_Asset-Level_Visibility.jpg" alt="Extending Point One Navigation to Ubiquitous Asset Tracking">
  <br>
  <em>Image credit: Richard Lourette and Grok</em>
</p>

**Version 2.8 | December 2025**

**Author:** Richard W. Lourette  
**Contact:** rlourette_at_gmail.com  
**Location:** Fairport, New York, USA

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 2025 | R. Lourette | Initial draft: core architecture, BLE mesh concept |
| 2.0 | December 2025 | R. Lourette | Added self-locating mesh, Kalman filtering, trilateration |
| 2.1 | December 2025 | R. Lourette | Enhanced API integration, P1 Tags feature alignment |
| 2.2 | December 2025 | R. Lourette | Pushed to Github |
| 2.5 | December 2025 | R. Lourette | Protocol coexistence (Eddystone-EID + Channel Sounding), tag portfolio strategy, mathematical appendix, glossary expansion |
| 2.6 | December 2025 | R. Lourette | Autonomous mesh creation |
| 2.7 | December 2025 | R. Lourette | Visual-inertial mesh localization (Section 4.6), unified fiducial/beacon reference nodes, P1 Positioning Engine integration, tiered communication architecture with WiFi HaLow, Location as a Service (LaaS) business model, zero-infrastructure deployment emphasis, OEM hardware/licensed software model |
| 2.8 | December 2025 | R. Lourette | Starlink backhaul option, glossary expansion |

---

## A Note on Terminology

This paper proposes extending Point One Navigation's platform with physical asset tracking devices (BLE (Bluetooth Low Energy) beacons attached to pallets, boxes, and containers). These should not be confused with P1's existing **Tags feature**, which is a powerful API capability for attaching customer metadata to P1 devices and querying them via GraphQL.

Throughout this document:
- **P1 Tags** refers to the existing metadata/device management feature
- **Asset Beacons** refers to the proposed physical BLE tracking devices
- **Relay Nodes** refers to battery-powered gateways that bridge asset beacons to P1's network
- **Reference Nodes** refers to fiducial/beacon combinations that enable visual-inertial navigation
- **Infrastructure Nodes** refers to mains-powered aggregation points with high-bandwidth backhaul

This distinction matters: the P1 Tags feature becomes even more valuable when extended to manage tens of thousands of asset beacons alongside Global Navigation Satellite System (GNSS)-enabled devices.

---

## Executive Summary

Point One Navigation has built the world's most accessible centimeter-accurate positioning platform. With the Polaris RTK Network, Location Cloud API, and Positioning Engine, P1 delivers precise outdoor location for vehicles, robots, and connected devices. The recent \$35M Series C and stated goal to "solve ubiquitous location...eventually indoors and all domains" signals the next phase of growth.

This white paper proposes a practical path to indoor and asset-level tracking by integrating hybrid BLE-Thread-WiFi HaLow mesh networks with P1's existing infrastructure. The architecture enables:

- **Seamless outdoor-to-indoor handoff** using P1 gateways as mesh coordinators
- **Passive asset tracking** for pallets, boxes, and containers without per-item GNSS hardware
- **Self-locating relay mesh** that automatically derives anchor positions from nearby P1-enabled vehicles, eliminating manual surveying and enabling rapid deployment
- **Visual-inertial navigation** for forklifts and drones using camera observations of fiducial-equipped reference nodes
- **Scalable deployment** supporting 100,000+ tracked assets per facility
- **Location as a Service (LaaS)** revenue model with predictable recurring subscriptions

**Key Innovations:**

1. **Self-Locating Mesh:** Every P1-enabled vehicle (forklift, tractor, AGV) becomes a mobile positioning anchor. Using Bluetooth 6.0 Channel Sounding and Kalman filtering, relay nodes automatically derive their positions from passing P1 equipment, then use trilateration to locate asset tags. This eliminates the deployment friction that plagues traditional RTLS systems: no surveying, no per-anchor GNSS hardware, no recalibration when equipment moves.

2. **Visual-Inertial Enhancement:** Reference nodes combine visual fiducial markers with BLE beacons, enabling forklifts and drones running P1's Positioning Engine to maintain continuous navigation throughout indoor facilities. Camera observations of fiducials provide bearing and range fixes that correct IMU drift, while the mesh self-locates from one or two P1 RTK anchors. A facility can go from bare walls to sub-30cm positioning accuracy in under an hour with no surveying.

3. **Zero-Infrastructure Deployment:** The system requires no facility modifications: no conduit, no cabling, no network drops. Battery-powered nodes mount anywhere with adhesive or magnets. Mains-powered infrastructure nodes plug into existing outlets. Only the P1 gateway requires external connectivity (cellular, Starlink, or Ethernet to Location Cloud); all other nodes communicate wirelessly through the mesh. This dramatically reduces deployment cost and enables temporary, remote, or leased facilities where traditional IT infrastructure is unavailable or impractical.

4. **Tiered Communication Architecture:** Battery-powered relay nodes use Thread for low-power mesh networking, while mains-powered infrastructure nodes use WiFi HaLow (802.11ah) for high-bandwidth aggregation. This prevents Thread bandwidth saturation in large deployments while maintaining years of battery life for edge devices.

This approach complements P1's roadmap rather than competing with it, providing near-term indoor coverage while P1 develops more sophisticated positioning technologies.

---

## 1. The Ubiquitous Location Opportunity

### 1.1 P1's Current Strength

Point One has solved outdoor precision location at scale:

- 2,000+ professionally managed RTK base stations across North America, Europe, and Asia
- Centimeter-level accuracy through the Polaris network
- Single GraphQL API unifying corrections, telemetry, and device management
- 10x growth in Original Equipment Manufacturer (OEM) adoption over the past year
- Proven deployments: 150,000+ vehicles from one EV manufacturer, 300,000 last-mile delivery vehicles

### 1.2 The Indoor Gap

As P1 CEO Aaron Nathan stated in the November 2025 TechCrunch interview: *"What we're building next—and that's part of what this fundraising is for—is, how do we do long-term indoor navigation as well. When you look at the evolution of the business, we want to solve ubiquitous location, so eventually it will be indoors and all domains."*

Currently, P1's indoor capability is limited to short-term continuity: vehicles entering parking structures maintain position through dead reckoning and sensor fusion. This works for powered vehicles with IMUs and compute resources, but doesn't address:

- Warehouse robots that "spend the bulk of their life inside"
- Pallets and containers moving through distribution centers
- Assets transitioning between outdoor transport and indoor storage
- Temporary or rapidly deployed facilities

### 1.3 The Asset Tracking Dimension

Beyond indoor positioning, there's a parallel opportunity in **passive asset tracking**. P1's current customers (fleet operators, logistics companies, agricultural equipment manufacturers) don't just need to know where their vehicles are. They need to track what those vehicles carry:

- Which pallets are on which trailer?
- Where is a specific container in the warehouse?
- Has this shipment moved from dock to storage to outbound staging?

This visibility requires tracking assets that can't carry GNSS receivers: coin-cell-powered beacons on pallets, boxes, and containers.

### 1.4 The Deployment Friction Problem

Traditional Real-Time Location Systems (RTLS) suffer from a fundamental deployment barrier: every anchor point must have a precisely known position. This means either:

- **Expensive per-anchor GNSS hardware** (\$500-2000 per anchor), or
- **Time-consuming manual surveying** that must be repeated whenever equipment moves

This friction limits RTLS adoption to permanent, high-value installations. Temporary facilities, seasonal overflow, and rapidly reconfigured spaces are impractical to serve.

**P1's Unique Opportunity**

P1 customers already operate fleets of equipment with centimeter-accurate RTK positioning: forklifts, tractors, AGVs, yard trucks. These vehicles continuously receive Polaris corrections and know their positions precisely. This paper proposes leveraging that existing infrastructure as a **distributed positioning network**.

The key insight: relay nodes can automatically derive their positions from nearby P1-enabled equipment using Bluetooth 6.0 Channel Sounding and sensor fusion algorithms. As P1 vehicles traverse the facility, they "donate" their positions to stationary relay nodes. The relay nodes then use trilateration to locate passive asset tags.

This **self-locating mesh** architecture eliminates surveying entirely. Deploy relay nodes, let P1 vehicles drive past, and the system self-calibrates. Move a relay node? It automatically re-localizes. Set up a temporary facility? The mesh configures itself as equipment operates.

No other RTLS vendor can offer this capability. It requires the combination of widespread RTK-equipped vehicles and a unified positioning platform that P1 uniquely possesses.

---

## 2. Proposed Architecture

### 2.1 System Components

The hybrid architecture introduces four new device classes that integrate with P1's existing platform:

**Asset Beacons (Coin Cell Powered)**
- BLE 5.x/6.0 devices attached to pallets, boxes, or containers
- Transmit encrypted Eddystone-EID or Channel Sounding signals
- 8-12 month battery life on CR2032
- Zero configuration required: activate and attach
- **Installation:** Adhesive backing or zip tie; no infrastructure needed
- Cost target: \$5-15 per beacon at scale

**Relay Nodes (Battery Powered)**
- Dual-radio devices: BLE scanner + Thread mesh networking
- Deployed on warehouse ceilings, pallet racks, or vehicle-mounted
- Forward beacon detections to infrastructure nodes via Thread mesh
- Battery-powered: 12+ month life on 1200mAh cell
- Can incorporate P1's Positioning Engine for precise self-location
- **Installation:** Magnetic mount, adhesive, or zip tie; no wiring required

**Reference Nodes (Fiducial + Beacon)**
- Combined visual fiducial marker (AprilTag/ArUco) and BLE 6.0 beacon
- Self-locating via mesh ranging from P1 anchors
- Broadcasts computed position for vehicle INS aiding
- Camera-detectable for visual navigation updates
- Battery life: 3-5 years
- **Installation:** Screw mount or adhesive on columns/walls; no wiring required
- Cost target: \$30-50 per node

**Infrastructure Nodes (Mains Powered)**
- High-bandwidth aggregation points with WiFi HaLow (802.11ah) connectivity
- Bridge between Thread mesh edge and P1 gateways
- Support 50-100+ asset tag detections per second
- **Installation:** Plug into any standard outlet; no network connection required
- Cost target: \$100-200 per node

**P1 Gateways (Existing + Enhanced)**
- WiFi HaLow access point functionality added to P1 devices
- Bridge between facility mesh and P1's Location Cloud API
- Provide GNSS-derived position context for all detections
- **Installation:** Single device requiring external connectivity (cellular, Starlink, or Ethernet)
- Existing P1 customers already have gateway hardware deployed

### 2.2 Data Flow

The architecture leverages Polaris-connected gateways as geographic anchors. Every indoor detection inherits real-world coordinates from gateways that know their precise position via Polaris RTK corrections.

```mermaid
flowchart LR
    subgraph Sources["Asset Layer"]
        AB[/"🏷️ Asset Beacon<br/>(BLE)"/]
    end
    
    subgraph Edge["Edge Mesh"]
        RN[["📡 Relay Node<br/>(Thread)"]]
    end
    
    subgraph Aggregation["Aggregation Layer"]
        INF[["📶 Infrastructure Node<br/>(WiFi HaLow)"]]
    end
    
    subgraph Infrastructure["P1 Infrastructure"]
        GW[("🛰️ P1 Gateway<br/>(Polaris)")]
        API["☁️ Location Cloud<br/>API"]
    end
    
    subgraph Customer["Customer"]
        DASH["📊 Dashboard"]
    end
    
    AB -->|"BLE CS +<br/>Eddystone-EID"| RN
    RN -->|"Thread<br/>250 kbps"| INF
    INF -->|"WiFi HaLow<br/>2-30 Mbps"| GW
    GW -->|"HTTPS/WSS"| API
    API -->|"Real-time<br/>events"| DASH
    
    style AB fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b
    style RN fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    style INF fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px,color:#1a237e
    style GW fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    style API fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    style DASH fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#880e4f
    
    style Sources fill:#e3f2fd,stroke:#1976d2,stroke-width:1px
    style Edge fill:#f3e5f5,stroke:#8e24aa,stroke-width:1px
    style Aggregation fill:#e8eaf6,stroke:#5c6bc0,stroke-width:1px
    style Infrastructure fill:#e8f5e9,stroke:#43a047,stroke-width:1px
    style Customer fill:#fce4ec,stroke:#d81b60,stroke-width:1px
```

**Data Flow Summary:**

| Component | Function | Protocol | Bandwidth |
|-----------|----------|----------|-----------|
| **Asset Beacon** | Transmits identity + ranging | BLE 6.0 | ~1 Mbps burst |
| **Relay Node** | Edge aggregation | Thread | 250 kbps shared |
| **Infrastructure Node** | High-bandwidth aggregation | WiFi HaLow | 2-30 Mbps |
| **P1 Gateway** | Cloud backhaul + RTK anchor | Cellular/Starlink/Ethernet | 10+ Mbps |
| **Location Cloud** | Aggregates & serves | HTTPS/GraphQL | Unlimited |

**Detection Event Payload:**
- Asset beacon identifier (resolved from rotating EID)
- Detecting relay node ID
- RSSI or Channel Sounding distance measurement
- Gateway GNSS position and timestamp
- Mesh hop count and latency

### 2.3 Why This Architecture

**Leverages P1's existing infrastructure:** Gateways already deployed for GNSS correction delivery become mesh coordinators. The Location Cloud API already handles device management, telemetry, and customer queries. Asset beacon detections are simply a new event type.

**Separates concerns appropriately:** Ultra-low-power beacons do one thing well (transmit identity). Relay nodes handle the complexity of mesh networking. Infrastructure nodes provide bandwidth aggregation. P1's cloud handles resolution, aggregation, and customer integration.

**Scales efficiently:** Thread mesh provides coverage redundancy and self-healing at the edge. WiFi HaLow prevents bandwidth bottlenecks at aggregation points. The system handles 100,000+ assets per facility.

---

## 3. Gateway Deployment Scenarios

P1 gateways become the bridge between GNSS-accurate outdoor positioning and indoor asset visibility. Deployment scenarios include:

### 3.1 Fixed Infrastructure

**Warehouse Ceilings**
- Mains-powered gateways with WiFi HaLow access point capability
- Polaris RTK corrections provide survey-grade self-location (centimeter-accurate facility reference point)
- Aggregate detections from infrastructure nodes throughout facility
- Typical density: 1 gateway per 50,000 sq ft, infrastructure nodes every 100 ft, relay nodes every 50 ft

**Distribution Center Docks**
- Track asset handoff between transport and storage
- Capture the moment pallets move from trailer to facility
- Integration with WMS for automated receiving

### 3.2 Mobile Platforms

**Tractor Trailers**
- Vehicle-mounted P1 gateway with integrated relay node
- Tracks which pallets/containers are loaded
- Provides in-transit visibility with GNSS position
- Detects loading/unloading events automatically

**Aircraft Cargo**
- Ruggedized gateway for air transport containers
- Tracks ULD (Unit Load Device) contents
- Enables chain-of-custody documentation

### 3.3 Temporary Deployments

**Disaster Relief Operations**
- Rapidly deployed gateway + relay node kits
- Track medical supplies, equipment, and provisions
- No permanent infrastructure required
- Cellular/Starlink backhaul to P1 cloud

**Pop-up Warehouses / Seasonal Overflow**
- Battery-powered mesh deployed in hours
- Full asset visibility without facility modification
- Recover and redeploy as needs change

### 3.4 Relay Node Position Anchoring via P1-Enabled Devices

A key architectural innovation: relay nodes can obtain their own position from nearby P1-enabled equipment rather than requiring individual GNSS receivers or manual surveying.

**The Challenge**

Traditional RTLS systems require each anchor point to have a precisely surveyed position. This creates deployment friction: either expensive GNSS hardware in every anchor, or time-consuming manual surveying that must be repeated whenever equipment moves.

**The P1 Advantage**

Many P1 customers already operate fleets of P1-enabled equipment: forklifts in warehouses, tractors in agriculture, AGVs in manufacturing, service vehicles in logistics. These devices continuously receive Polaris RTK corrections and maintain centimeter-accurate position. This existing infrastructure becomes a distributed positioning network.

**Position Donation Protocol**

```mermaid
sequenceDiagram
    participant F as 🚜 Forklift<br/>(P1-Enabled)
    participant R as 📡 Relay Node<br/>(on rack)
    participant C as ☁️ Location Cloud

    Note over F: RTK Position: 47.6205°, -122.3493°<br/>Accuracy: ±0.02m

    F->>R: BLE Advertisement (P1 device present)
    R->>F: Channel Sounding Request
    F->>R: Channel Sounding Response
    
    Note over F,R: Distance measured: 3.2m @ 47°

    F->>R: Position Donation Message<br/>(lat, lon, alt, accuracy, timestamp)
    
    Note over R: Calculate own position:<br/>Relay = Forklift + Offset Vector<br/>= 47.6205°, -122.3493° + (3.2m @ 47°)

    R->>C: Thread Mesh: Position Update<br/>(relay_id, derived_position, confidence)
    C->>C: Store relay position<br/>Average with previous observations

    Note over R: Relay now has known position<br/>Can estimate asset tag locations
```

**How It Works:**

1. **P1-enabled device** (forklift, AGV, tractor) operates in the facility with RTK positioning active
2. **Proximity detection:** When the device comes within BLE range of a relay node, both devices recognize each other
3. **Channel Sounding exchange:** The P1 device and relay node perform a Channel Sounding measurement to determine precise distance and (with multiple antennas) direction
4. **Position transfer:** The P1 device shares its current RTK position with the relay node via BLE or Thread
5. **Relay node calculation:** The relay computes its own position using sensor fusion algorithms (see Section 4.4)
6. **Position refinement:** As multiple P1 devices pass by over time, the estimate converges to high accuracy

This approach transforms every P1-enabled vehicle into a mobile positioning anchor, extending RTK-grade accuracy from the vehicle to the assets around it. The technical details of position estimation, including Kalman filtering, trilateration, and self-locating mesh algorithms, are covered in Section 4.4.

For deployments with camera-equipped vehicles (forklifts, drones, AGVs), reference nodes can include visual fiducial markers that provide an additional position observation source. See Section 4.6 for the visual-inertial architecture that leverages both radio and camera-based position updates.

---

## 4. Enabling Technologies

### 4.1 Bluetooth 6.0 Channel Sounding

Released September 2024, Bluetooth 6.0 introduces Channel Sounding, a game-changing capability for indoor positioning:

**Phase-Based Ranging (PBR):** Measures phase differences across 72 channels in the 2.4 GHz band to calculate distance with 10-centimeter accuracy using single-antenna hardware.

**Round-Trip Time (RTT):** Provides cryptographically secured timing measurements that cross-verify PBR results and prevent relay attacks.

**Why This Matters for P1:**
- Asset beacons can provide not just presence detection but precise distance to relay nodes
- Zone-level positioning without expensive infrastructure (no Quuppa-style antenna arrays)
- Security features align with P1's emphasis on authenticated, secure positioning
- Silicon shipping now: Nordic nRF54, Silicon Labs xG24, Qualcomm Snapdragon 8 Elite

Channel Sounding means the system can answer "pallet X is 2.3 meters from relay node Y" rather than just "pallet X was detected by relay node Y," enabling true indoor positioning from the asset beacon layer.

### 4.2 Thread / Matter over Thread

Thread provides the mesh backhaul for battery-powered relay node communication:

**IPv6 Native:** Direct integration with P1's GraphQL API without protocol translation. Thread devices get routable IP addresses.

**Self-Healing Mesh:** No single point of failure. Relay nodes automatically route around failures.

**Low Power:** Thread Sleepy End Devices can achieve multi-year battery life while maintaining mesh connectivity.

**Industry Momentum:** IKEA announced 21 Matter-over-Thread devices (November 2025). Apple, Google, Amazon all shipping Thread Border Routers. Nordic and Silicon Labs have mature OpenThread implementations.

**Bandwidth Limitation:** Thread's 250 kbps is shared across the mesh. This is adequate for battery-powered relay nodes handling 10-20 nearby tags, but insufficient for mains-powered infrastructure nodes aggregating hundreds of detections per second. See Section 4.7 for the tiered communication architecture that addresses this.

### 4.3 Eddystone-EID for Privacy and Security

Asset beacons transmit rotating encrypted identifiers (Eddystone-EID) rather than static IDs:

- Prevents tracking by unauthorized parties
- Identity resolution happens at P1 cloud with customer-specific keys
- Relay nodes can cache resolutions for offline operation
- Aligns with P1's security-first architecture

### 4.4 Self-Locating Mesh Architecture

This section details the sensor fusion algorithms that enable relay nodes to determine their own positions automatically. This key innovation eliminates manual surveying and enables rapid deployment.

**The Challenge**

A single range measurement from one P1 device provides only a noisy position estimate. Real-world deployments face multipath reflections, NLOS (non-line-of-sight) conditions, and varying measurement quality. The solution is recursive state estimation using Kalman filtering and related techniques.

**Extended Kalman Filter (EKF) for Relay Position Estimation**

Each relay node maintains a state estimate of its own position along with an uncertainty measure. As P1 devices pass by and donate their positions, the EKF fuses these observations to progressively refine the relay's position estimate. The filter automatically weights each observation based on its expected accuracy and rejects outliers that are inconsistent with the current estimate.

The EKF is well-suited for this application because it handles noisy measurements, adapts to varying P1 device accuracy, and converges quickly even when starting with no prior position knowledge. For mathematical details, see Appendix A.

**Convergence Behavior:**

| Observations | Typical Uncertainty | Use Case |
|-------------|---------------------|----------|
| 1 | ±0.5m | Initial estimate |
| 3-5 | ±0.2m | Operational accuracy |
| 10+ | ±0.1m | High confidence |
| 50+ | ±0.05m | Survey-grade |

**Alternative Estimation Approaches**

For scenarios where standard assumptions do not hold, alternative algorithms may be employed:

- **Particle Filter:** Handles non-Gaussian noise distributions common in indoor RF environments by maintaining multiple position hypotheses
- **Factor Graph Optimization:** Solves for globally consistent positions across the entire relay mesh simultaneously
- **Weighted Least Squares:** Batch approach suitable for periodic position recalculation

See Appendix A for detailed descriptions of these algorithms.

**Relay-to-Relay Ranging for Self-Locating Mesh**

The positioning fabric becomes truly self-locating when relay nodes can also range to each other:

```mermaid
flowchart LR
    subgraph SelfLocating["Self-Locating Relay Mesh"]
        P1["🚜 P1 Device<br/>RTK Position Known"]
        
        R1["📡 Relay 1"]
        R2["📡 Relay 2"]
        R3["📡 Relay 3"]
        R4["📡 Relay 4"]
        
        P1 -->|"CS: 2.1m"| R1
        P1 -.->|"occasional"| R3
        
        R1 <-->|"CS: 4.5m"| R2
        R1 <-->|"CS: 6.2m"| R3
        R2 <-->|"CS: 3.8m"| R3
        R2 <-->|"CS: 5.1m"| R4
        R3 <-->|"CS: 4.9m"| R4
    end
    
    style P1 fill:#c8e6c9,stroke:#43a047,stroke-width:2px
    style R1 fill:#e3f2fd,stroke:#1976d2
    style R2 fill:#e3f2fd,stroke:#1976d2
    style R3 fill:#e3f2fd,stroke:#1976d2
    style R4 fill:#e3f2fd,stroke:#1976d2
```

**How Relay-to-Relay Ranging Helps:**

1. **Position propagation:** Relay 1 gets position from P1 device. Relay 2 ranges to Relay 1, derives its own position. Relay 4 (never sees P1 device) still gets positioned via the chain.

2. **Redundancy:** Multiple paths to position each relay improves accuracy and detects inconsistencies.

3. **Geometric constraints:** Inter-relay distances constrain the solution space, enabling factor graph optimization across the entire mesh.

4. **Drift detection:** If a relay is accidentally moved, its inter-relay distances change, triggering re-localization.

**Implementation Considerations:**

- **Compute location:** EKF runs on-device for real-time updates; factor graph optimization runs in Location Cloud for global consistency
- **Update frequency:** Position donations occur opportunistically; inter-relay ranging can be scheduled hourly to conserve power
- **Bootstrapping:** New relay nodes start with high uncertainty; system prioritizes routing P1 devices past unlocalized relays
- **Outlier rejection:** Mahalanobis distance gating rejects statistically inconsistent measurements

**Trilateration for Asset Tag Positioning**

Once relay nodes know their own positions, they can estimate the location of passive asset tags using trilateration, which computes position from distance measurements to three or more known reference points:

```mermaid
flowchart TB
    subgraph Trilateration["Asset Position via Trilateration"]
        direction TB
        
        RA["📡 Relay A<br/>Position: Known<br/>47.6205°, -122.3492°"]
        RB["📡 Relay B<br/>Position: Known<br/>47.6204°, -122.3495°"]
        RC["📡 Relay C<br/>Position: Known<br/>47.6207°, -122.3494°"]
        
        TAG["📦 Asset Tag<br/>(Pallet)"]
        
        RA -->|"2.1m @ 315°"| TAG
        RB -->|"3.4m @ 127°"| TAG
        RC -->|"4.2m @ 045°"| TAG
        
        RESULT["✅ Computed Position<br/>47.6205°, -122.3494°<br/>Accuracy: ±0.15m"]
        TAG --> RESULT
    end

    style RA fill:#e3f2fd,stroke:#1976d2
    style RB fill:#e3f2fd,stroke:#1976d2
    style RC fill:#e3f2fd,stroke:#1976d2
    style TAG fill:#fff3e0,stroke:#f57c00
    style RESULT fill:#e8f5e9,stroke:#43a047
```

**Accuracy Scaling:**

| Relay Observations | Typical Accuracy | Use Case |
|-------------------|------------------|----------|
| Single relay | ±0.5m | Zone identification |
| Two relays | ±0.3m | Aisle-level positioning |
| Three+ relays | ±0.15m | Slot-level positioning |

**Deployment Benefits vs. Traditional RTLS:**

| Aspect | Traditional RTLS | P1 Self-Locating Mesh |
|--------|------------------|----------------------|
| **Anchor positioning** | Manual survey or per-anchor GNSS | Automatic via mobile P1 devices |
| **Deployment time** | Days (surveying) | Hours (self-configuring) |
| **Anchor hardware cost** | \$500-2000/anchor | \$50-100/relay node |
| **Position updates** | Static (requires re-survey) | Dynamic (continuous refinement) |
| **Mobile deployments** | Difficult | Native capability |
| **Facility modifications** | Conduit, cabling, network drops | None (wireless mesh) |
| **External connectivity** | Per-anchor or controller | Single P1 gateway only |

The self-locating mesh can be further enhanced when mobile platforms carry cameras. By integrating visual fiducial markers into reference nodes, vehicles gain an additional observation source for INS aiding. This visual-inertial approach is detailed in Section 4.6.

### 4.5 Protocol Coexistence on Asset Tags

A common question: can a single asset tag support both Eddystone-EID (secure identity) and Channel Sounding (precision ranging)? The answer is yes. These protocols serve complementary functions and coexist naturally on modern BLE 6.0 silicon.

**How Both Protocols Operate on One Device**

```mermaid
flowchart LR
    subgraph AssetTag["BLE 6.0 Asset Tag (e.g., nRF54L15)"]
        direction TB
        ADV["Advertising Engine"]
        CS["Channel Sounding Reflector"]
    end
    
    subgraph Channels["BLE Radio Channels"]
        ADV_CH["Advertising Channels<br/>(37, 38, 39)"]
        DATA_CH["Data Channels<br/>(0-36)"]
    end
    
    subgraph Relay["Relay Node"]
        SCAN["Scanner"]
        CSI["CS Initiator"]
    end
    
    ADV -->|"Eddystone-EID<br/>Broadcast"| ADV_CH
    ADV_CH -->|"Identity"| SCAN
    
    CSI -->|"CS Request"| DATA_CH
    DATA_CH -->|"Tone Exchange"| CS
    CS -->|"CS Response"| DATA_CH
    DATA_CH -->|"Distance: 3.2m"| CSI
    
    style AssetTag fill:#e3f2fd,stroke:#1976d2
    style Relay fill:#c8e6c9,stroke:#43a047
```

**Protocol Functions:**

| Protocol | Purpose | Radio Usage | Power Impact |
|----------|---------|-------------|--------------|
| Eddystone-EID | Secure identity broadcast | Advertising channels, periodic beacon | Low (passive broadcast) |
| Channel Sounding | Precision distance measurement | Data channels, on-demand response | Moderate (only when queried) |

The two protocols use different radio channels and serve different purposes:

1. **Eddystone-EID** broadcasts on advertising channels (37, 38, 39) at configurable intervals, typically every 1-10 seconds. The rotating encrypted identifier enables secure detection without pairing.

2. **Channel Sounding** operates on data channels (0-36) only when a relay node initiates a ranging session. The tag acts as a reflector, responding to tone sequences to enable distance calculation.

Because advertising and data channel operations are independent, a tag can broadcast its identity continuously while responding to ranging requests as they arrive. The BLE stack handles channel switching automatically.

**Asset Tag Product Tiers**

This protocol flexibility enables a tiered product strategy:

| Tier | Protocols | Accuracy | Battery Life | Target Price | Use Case |
|------|-----------|----------|--------------|--------------|----------|
| **Basic** | Eddystone-EID only | Zone (±3m via RSSI) | 36+ months | \$5-8 | Presence detection, zone transitions |
| **Standard** | Eddystone-EID + CS Reflector | Sub-meter (±0.3m) | 18-24 months | \$12-18 | Aisle-level tracking, inventory |
| **Precision** | Eddystone-EID + CS + IMU | Centimeter (±0.1m) | 12-18 months | \$25-40 | High-value assets, AGV coordination |

All tiers share the same secure identity infrastructure and Location Cloud integration. The difference lies in positioning accuracy and hardware cost, allowing customers to match tag capability to asset value.

### 4.6 Visual-Inertial Mesh Localization

This section describes how camera-equipped vehicles (forklifts, drones, AGVs) can leverage visual observations of fiducial-equipped reference nodes to maintain continuous, drift-free navigation throughout indoor facilities using P1's Positioning Engine.

#### 4.6.1 Unified Fiducial/Beacon Reference Nodes

The self-locating mesh architecture is enhanced by combining visual fiducial markers with BLE 6.0 beacons into unified reference nodes. This dual-mode approach provides redundant position observation sources for mobile platforms operating within the mesh.

**Integrated Reference Node Design**

```mermaid
flowchart TB
    subgraph RefNode["Unified Reference Node"]
        direction TB
        VIS["Visual Fiducial<br/>(AprilTag/ArUco)<br/>Encodes Node ID"]
        BLE["BLE 6.0 Beacon<br/>• Broadcasts Position<br/>• CS Reflector<br/>• Mesh Participant"]
        BAT["Battery: 3-5 Years"]
    end
    
    subgraph Functions["Dual Functions"]
        F1["Mesh Self-Location<br/>(peer-to-peer CS ranging)"]
        F2["Vehicle INS Aiding<br/>(camera observation)"]
        F3["Position Broadcast<br/>(BLE advertisement)"]
    end
    
    RefNode --> F1
    RefNode --> F2
    RefNode --> F3
    
    style RefNode fill:#e3f2fd,stroke:#1976d2
    style VIS fill:#fff3e0,stroke:#f57c00
    style BLE fill:#e8f5e9,stroke:#43a047
```

Each reference node serves three functions:

| Function | Mechanism | Benefit |
|----------|-----------|---------|
| Mesh participant | BLE CS ranging to P1 anchor and peer nodes | Self-locates without surveying |
| Position broadcaster | BLE advertisement with computed coordinates | Vehicles receive position instantly |
| Visual landmark | Camera-detectable fiducial pattern | INS aiding for drift correction |

**Why Dual-Mode Matters**

Camera and radio provide complementary observation characteristics:

| Observation Source | Strengths | Limitations |
|-------------------|-----------|-------------|
| Camera + Fiducial | Accurate bearing and elevation; works in RF-noisy environments | Requires line-of-sight; affected by lighting |
| BLE Channel Sounding | Works without line-of-sight; consistent in varying light | Subject to multipath; requires radio |

When both are available, the vehicle's navigation filter gains redundancy. If one modality fails (camera occluded, BLE interference), the other maintains position continuity.

#### 4.6.2 Vehicle Navigation Architecture

Forklifts, drones, and AGVs operating within the mesh run **P1's Positioning Engine**, the same sensor fusion system that provides centimeter-accurate outdoor navigation. Indoors, the Positioning Engine substitutes visual fiducial observations and BLE Channel Sounding ranges for GNSS satellite signals, using identical Kalman filtering mathematics.

```mermaid
flowchart LR
    subgraph Sensors["Onboard Sensors"]
        IMU["IMU<br/>(100+ Hz)"]
        CAM["Camera<br/>(30 Hz)"]
        BLE["BLE 6.0 CS<br/>(1-10 Hz)"]
        WHEEL["Wheel Odometry<br/>(50 Hz)"]
    end
    
    subgraph External["External References"]
        P1_RTK["P1 RTK<br/>(outdoor)"]
        REF["Reference Nodes<br/>(indoor)"]
    end
    
    subgraph Filter["P1 Positioning Engine"]
        STATE["State Vector:<br/>• Position (x,y,z)<br/>• Velocity<br/>• Attitude<br/>• Sensor Biases"]
    end
    
    subgraph Output["Outputs"]
        POS["Vehicle Position<br/>(continuous)"]
        DONATE["Position Donation<br/>(to mesh)"]
    end
    
    IMU --> Filter
    CAM --> Filter
    BLE --> Filter
    WHEEL --> Filter
    P1_RTK --> Filter
    REF --> Filter
    
    Filter --> POS
    Filter --> DONATE
    
    style Filter fill:#c8e6c9,stroke:#43a047,stroke-width:2px
```

**Why P1's Positioning Engine**

This architecture leverages P1's core technology investment rather than building parallel systems:

| Capability | Outdoor (Current) | Indoor (Proposed) |
|------------|-------------------|-------------------|
| Primary aiding source | GNSS satellites | Visual fiducials + BLE CS |
| Correction source | Polaris RTK network | Self-locating mesh |
| Sensor fusion | P1 Positioning Engine | P1 Positioning Engine |
| Output API | Location Cloud GraphQL | Location Cloud GraphQL |

The Positioning Engine already handles IMU integration, outlier rejection, and multi-source fusion. Adding camera and BLE observation types extends its capability without architectural changes.

**Observation Sources by Environment**

| Environment | Primary Aiding | Secondary Aiding | IMU Role |
|-------------|---------------|------------------|----------|
| Outdoor (sky view) | P1 RTK GNSS | Wheel odometry | Bridge brief outages |
| Transition (dock door) | RTK → Reference nodes | Camera fiducials | Smooth handoff |
| Indoor (warehouse) | Camera fiducials | BLE CS to reference nodes | Dead reckon between fixes |
| Indoor (obstructed) | BLE CS ranging | — | Extended dead reckoning |

#### 4.6.3 Camera-Based Position Update

When the vehicle camera detects a fiducial on a reference node, the navigation filter performs a measurement update:

**Observation Extraction**

From camera image:
- Node ID (decoded from fiducial pattern)
- Bearing (horizontal angle from camera centerline)
- Elevation (vertical angle from camera centerline)
- Range estimate (from apparent fiducial size)
- Relative orientation (fiducial face normal)

From reference node broadcast:
- Node position (X, Y, Z) in facility frame
- Position uncertainty (from mesh solution)

**Measurement Model**

The filter compares observed bearing/elevation/range against predicted values computed from the current state estimate and known node position:

```
Predicted bearing   = atan2(Ynode - Yvehicle, Xnode - Xvehicle) - yaw
Predicted elevation = atan2(Znode - Zvehicle, horizontal_distance)
Predicted range     = sqrt((ΔX)² + (ΔY)² + (ΔZ)²)

Innovation = Observed - Predicted
```

The Kalman gain weights the correction based on observation quality (image sharpness, range confidence) and current state uncertainty. Poor observations have minimal impact; high-quality observations snap the estimate to ground truth.

**Accuracy Characteristics**

| Observation | Typical Accuracy | Notes |
|-------------|-----------------|-------|
| Bearing from image | ±0.5° | Limited by camera resolution and calibration |
| Elevation from image | ±0.5° | Same factors as bearing |
| Range from fiducial size | ±5-10% | Degrades with distance; augmented by BLE CS |
| Combined position fix | ±10-30cm | With reference node position known to ±20cm |

#### 4.6.4 Facility Self-Mapping Sequence

The complete deployment sequence requires minimal manual effort and **zero facility modifications**:

**Step 1: P1 Anchor Installation (minutes)**

Install one or two P1 nodes at locations with sky view (loading docks, exterior doors). These establish the absolute coordinate frame via RTK. This is the only equipment requiring external network connectivity (cellular, Starlink, or Ethernet to Location Cloud).

**Step 2: Reference Node Deployment (hours)**

Mount fiducial/beacon reference nodes throughout the facility on columns, rack uprights, walls, or ceilings. No surveying required, just place and power on. Battery-powered nodes require no wiring; simply attach with adhesive, magnets, or screws.

**Step 3: Mesh Self-Localization (automatic, minutes)**

```mermaid
sequenceDiagram
    participant P1 as P1 Node<br/>(RTK Anchor)
    participant R1 as Reference<br/>Node 1
    participant R2 as Reference<br/>Node 2
    participant R3 as Reference<br/>Node 3
    participant Cloud as Location<br/>Cloud

    Note over P1: Position known<br/>via RTK
    
    P1->>R1: CS Range: 12.3m
    P1->>R2: CS Range: 18.7m
    
    R1->>R2: CS Range: 8.2m
    R1->>R3: CS Range: 15.1m
    R2->>R3: CS Range: 11.4m
    
    R1->>Cloud: Range observations
    R2->>Cloud: Range observations
    R3->>Cloud: Range observations
    
    Cloud->>Cloud: Graph optimization
    
    Cloud->>R1: Position: (X1, Y1, Z1)
    Cloud->>R2: Position: (X2, Y2, Z2)
    Cloud->>R3: Position: (X3, Y3, Z3)
    
    Note over R1,R3: All nodes now know<br/>their positions
```

Reference nodes within range of the P1 anchor get direct position fixes. Nodes beyond P1 range derive positions through peer-to-peer ranging. The graph optimization (running in Location Cloud) solves for globally consistent positions across the entire mesh.

**Step 4: Vehicle Operation (continuous)**

Vehicles with cameras observe fiducials as they operate. Each observation:
- Updates the vehicle's INS state
- Optionally contributes a "reverse observation" that can refine the reference node's position
- Enables the vehicle to range to and locate asset tags

**Convergence Timeline**

| Milestone | Time | Accuracy |
|-----------|------|----------|
| P1 anchor online | Immediate | RTK (±2cm) |
| Nearby nodes positioned | 1-5 minutes | ±30-50cm |
| Full mesh converged | 5-30 minutes | ±20-30cm throughout |
| Vehicle operation refining mesh | Ongoing | ±10-20cm (improves over days) |

#### 4.6.5 Practical Considerations

**Reference Node Placement**

| Location | Advantages | Considerations |
|----------|------------|----------------|
| Column faces | Visible from aisles; protected from impacts | Multiple faces may need nodes for full coverage |
| Rack uprights | Regular spacing; existing structure | May be occluded by inventory |
| Ceiling | Unobstructed view; ideal for drones | Requires ladder/lift for installation |
| Wall-mounted | Easy installation; good for perimeter | Limited coverage depth |

**Fiducial Design Requirements**

- Unique ID encoded in visual pattern (AprilTag 36h11 or ArUco dictionary)
- Minimum size for detection at 10-20m range: ~15-20cm
- High contrast (black/white) for robust detection in variable lighting
- ID matches beacon's BLE identifier for unambiguous association

**Camera Requirements (vehicle-mounted)**

| Parameter | Minimum | Recommended |
|-----------|---------|-------------|
| Resolution | 640×480 | 1280×720 or higher |
| Frame rate | 15 fps | 30 fps |
| Field of view | 60° horizontal | 90°+ (wide angle) |
| Mounting | Fixed, forward-facing | Multiple cameras for 360° coverage |

**Power Budget (reference node)**

| Component | Active | Sleep | Duty Cycle | Average |
|-----------|--------|-------|------------|---------|
| BLE advertising | 15mA | — | 0.1% | 15µA |
| CS reflector | 20mA | — | 0.05% | 10µA |
| Mesh ranging | 25mA | — | 0.1% | 25µA |
| Processor | 5mA | 2µA | 0.5% | 30µA |
| **Total** | | | | **~80µA** |

At 80µA average, a 2000mAh battery provides 3+ years of operation.

### 4.7 Tiered Communication Architecture

The mesh network requires different communication technologies at different tiers, matched to power availability and data throughput requirements.

**The Thread Bandwidth Challenge**

Thread's 250 kbps is shared across the mesh. A battery-powered relay handling 10 tags at 1 update/second with 100-byte packets consumes only ~8 kbps, well within budget. But a mains-powered infrastructure node aggregating:

- 100 asset tag detections × 10/second × 50 bytes = 400 kbps (advertising)
- 50 CS range measurements × 1/second × 100 bytes = 40 kbps
- Mesh management overhead = 50 kbps

Total approaches 500 kbps, exceeding Thread's capacity.

**Solution: WiFi HaLow (802.11ah) for Infrastructure Tier**

```mermaid
flowchart TB
    subgraph Cloud["P1 Location Cloud"]
        API["GraphQL API"]
    end
    
    subgraph Infrastructure["Infrastructure Tier (Mains Powered)"]
        GW["P1 Gateway<br/>Cellular/Starlink/Ethernet"]
        INF1["Infrastructure Node<br/>WiFi HaLow"]
        INF2["Infrastructure Node<br/>WiFi HaLow"]
    end
    
    subgraph Relay["Relay Tier (Battery Powered)"]
        REL1["Relay Node<br/>Thread"]
        REL2["Relay Node<br/>Thread"]
        REL3["Relay Node<br/>Thread"]
    end
    
    subgraph Asset["Asset Tier (Coin Cell)"]
        TAG1["Asset Tag<br/>BLE 6.0"]
        TAG2["Asset Tag<br/>BLE 6.0"]
        TAG3["Asset Tag<br/>BLE 6.0"]
        TAG4["Asset Tag<br/>BLE 6.0"]
    end
    
    API <-->|"HTTPS/WSS"| GW
    GW <-->|"WiFi HaLow<br/>2-30 Mbps"| INF1
    GW <-->|"WiFi HaLow"| INF2
    
    INF1 <-->|"Thread<br/>250 kbps"| REL1
    INF1 <-->|"Thread"| REL2
    INF2 <-->|"Thread"| REL3
    
    REL1 <-.->|"BLE CS"| TAG1
    REL1 <-.->|"BLE CS"| TAG2
    REL2 <-.->|"BLE CS"| TAG3
    REL3 <-.->|"BLE CS"| TAG4
    
    style Cloud fill:#fff3e0,stroke:#f57c00
    style GW fill:#c8e6c9,stroke:#43a047,stroke-width:2px
    style INF1 fill:#e3f2fd,stroke:#1976d2
    style INF2 fill:#e3f2fd,stroke:#1976d2
```

**Protocol Selection by Tier**

| Tier | Power Source | Protocol | Bandwidth | Rationale |
|------|--------------|----------|-----------|-----------|
| Asset tags | Coin cell | BLE 6.0 | ~1 Mbps burst | Lowest power; broadcast + CS reflector only |
| Battery relays | AA/18650 | Thread | 250 kbps | Low power mesh; handles 10-20 nearby tags |
| Infrastructure nodes | Mains | WiFi HaLow | 2-30 Mbps | Aggregates 50-100+ tags; needs bandwidth |
| P1 Gateway | Mains | Cellular/Starlink/Ethernet | 10+ Mbps | Cloud backhaul; existing P1 infrastructure |

**WiFi HaLow (802.11ah) Benefits**

| Feature | Specification | Benefit |
|---------|---------------|---------|
| Frequency | Sub-1 GHz (902-928 MHz US) | 10× range vs 2.4 GHz; better wall penetration |
| Bandwidth | 1-8 MHz channels | 150 kbps to 30+ Mbps depending on range |
| Range | 100m-1km+ | Single AP covers large facility |
| Device capacity | 8,191 per AP | Scales to large deployments |
| Protocol | Native IPv6 | Direct cloud connectivity; no translation |
| Security | WPA3 | Enterprise-grade encryption |

Infrastructure nodes form a WiFi HaLow mesh among themselves, with one or more P1 gateways providing backhaul to Location Cloud. This eliminates the Thread bandwidth bottleneck while maintaining the low-power Thread mesh for battery-operated relay nodes.

**Connectivity Model**

A critical deployment advantage: **only the P1 gateway requires external network connectivity**. All other nodes communicate exclusively through the wireless mesh:

| Node Type | Power | Network Connection | Installation |
|-----------|-------|-------------------|--------------|
| Asset tags | Coin cell | None (BLE broadcast) | Attach to asset |
| Relay nodes | Battery | None (Thread mesh) | Mount anywhere |
| Reference nodes | Battery | None (BLE + Thread) | Mount on columns/walls |
| Infrastructure nodes | Mains outlet | None (WiFi HaLow mesh) | Plug into outlet |
| P1 Gateway | Mains outlet | Cellular, Starlink, or Ethernet | Single external connection |

This architecture requires **zero facility modifications**: no conduit runs, no Ethernet drops, no IT infrastructure changes. Battery nodes mount with adhesive, magnets, or zip ties. Mains-powered nodes plug into existing outlets. The P1 gateway's cellular or Starlink option means even the backhaul connection requires no facility network integration.

---

## 5. Integration with P1's Platform

### 5.1 Location Cloud API Extensions

Asset beacons integrate with P1's existing GraphQL API at `graphql.pointonenav.com`. The current API already provides the patterns needed for asset tracking; minimal extensions would support the full use case.

**Current P1 API Patterns (Production Today)**

P1's existing `myDevices` query with tag filtering provides the foundation:

```graphql
# Filter devices by tag (P1's existing capability)
query {
  myDevices(filter: { tag: { key: "Zone", value: { eq: "Receiving" } } }) {
    content {
      id
      label
      lastPosition {
        timestamp
        position { llaDec { lat lon alt } }
      }
    }
  }
}

# Real-time position updates via WebSocket subscription
subscription {
  devices {
    id
    lastPosition {
      timestamp
      position { llaDec { lat lon alt } }
    }
  }
}

# Attach customer metadata to any device
mutation {
  setDeviceTag(input: { 
    ids: ["beacon-a1b2c3"], 
    key: "SKU", 
    value: "PALLET-2024-0847" 
  }) { key value }
}
```

**Proposed Extensions for Asset Beacons**

Asset beacons would become a new device type within the existing schema. The extensions below illustrate how detections from relay nodes could be represented:

```graphql
# Conceptual extension: Query assets by facility/zone
query {
  myDevices(filter: { 
    and: [
      { deviceType: "ASSET_BEACON" },
      { tag: { key: "Facility", value: { eq: "warehouse-east" } } }
    ]
  }) {
    content {
      id
      label
      lastPosition {
        timestamp
        position { llaDec { lat lon alt } }
      }
      # Proposed extension fields
      detectionSource    # "relay_rssi" | "channel_sounding" | "gnss_gateway"
      detectingRelay { id label }
      signalStrength     # dBm or Channel Sounding distance (meters)
    }
  }
}

# Proposed: Subscribe to zone entry/exit events
subscription {
  assetEvents(zoneId: "zone-receiving-dock") {
    eventType    # "entered" | "exited" | "detected"
    device { id label }
    zone { id name }
    timestamp
  }
}
```

The key architectural insight: asset beacons are devices. They use the same provisioning, tagging, and query patterns as GNSS devices. The Location Cloud API already handles device management at scale; asset beacons represent a new device type, not a parallel system.

### 5.2 Leveraging P1 Tags for Asset Management

P1's existing Tags feature provides the customer integration layer for asset beacons. Using the current `setDeviceTag` mutation, customers can attach their own identifiers to beacon IDs:

```graphql
# Associate a beacon with customer's inventory system
mutation {
  setDeviceTag(input: { 
    ids: ["beacon-f7e2a1"], 
    key: "CustomerPO", 
    value: "PO-2025-847291" 
  }) { key value }
}

# Tag multiple beacons with shipment ID
mutation {
  setDeviceTag(input: { 
    ids: ["beacon-a1", "beacon-a2", "beacon-a3"], 
    key: "Shipment", 
    value: "SHIP-EAST-20251207" 
  }) { key value }
}

# Query all assets for a specific shipment
query {
  myDevices(filter: { 
    tag: { key: "Shipment", value: { eq: "SHIP-EAST-20251207" } }
  }) {
    content { id label lastPosition { position { llaDec { lat lon } } } }
  }
}
```

This approach means:

- No separate asset management system required
- Query assets using native customer terminology (PO numbers, SKUs, shipment IDs)
- Real-time synchronization via existing API patterns
- Customers control their own namespace (tag keys and values)

### 5.3 Unified Device Management

The Location Cloud already manages GNSS devices at scale. Asset beacons and relay nodes extend this:

- Provision beacons in bulk via API
- Monitor relay node health and battery status
- Manage Thread network topology
- Single dashboard for vehicles, gateways, relay nodes, and asset beacons

---

## 6. Business Model: Location as a Service

### 6.1 The LaaS Value Proposition

P1's business model extends naturally from corrections-as-a-service (Polaris RTK subscriptions) to **Location as a Service (LaaS)**, providing accurate, continuous position for any asset, anywhere, through a unified platform.

| What P1 Provides | Customer Outcome |
|------------------|------------------|
| RTK corrections network | Centimeter outdoor accuracy |
| Self-locating indoor mesh | Sub-meter indoor accuracy |
| Positioning Engine | Seamless indoor/outdoor handoff |
| Location Cloud API | Single integration point |
| Device management | Unified fleet + asset visibility |

Customers don't buy hardware and corrections separately; they subscribe to **location** for their assets.

### 6.2 Subscription Tiers

| Tier | Coverage | Accuracy | Example Use Case | Price Model |
|------|----------|----------|------------------|-------------|
| **Outdoor** | GNSS coverage | ±2cm (RTK) | Fleet vehicles, tractors | Per vehicle/month |
| **Facility** | Single site | ±30cm indoor | Warehouse, factory | Per facility/month |
| **Enterprise** | Multi-site | Full spectrum | Logistics network | Per asset under management |

**Facility Subscription Example**

A 100,000 sqft warehouse with:
- 2 P1 anchor nodes (loading docks)
- 50 reference nodes (fiducial + beacon)
- 10 infrastructure nodes (WiFi HaLow)
- 5,000 asset tags

**Traditional Model (Hardware + Per-Device):**
```
Hardware: $75,000 one-time
Software: $5,000/month (5,000 tags × $1)
Year 1 total: $135,000
```

**LaaS Model:**
```
Facility subscription: $8,000/month
Includes: Hardware lease, maintenance, software, support
3-year commitment: $288,000 total
```

The LaaS model:
- Lowers customer barrier to entry (no Capital Expenditure (CapEx))
- Creates predictable recurring revenue for P1
- Aligns incentives (P1 benefits from system reliability)
- Enables technology refresh without customer repurchase

### 6.3 Revenue Composition

```mermaid
pie title P1 Location Revenue Mix (Projected Year 3)
    "Outdoor RTK Subscriptions" : 40
    "Indoor Facility Subscriptions" : 25
    "Asset Tracking (per-tag)" : 20
    "Professional Services" : 10
    "Hardware Sales" : 5
```

**Key Metrics**

| Metric | Target |
|--------|--------|
| Monthly recurring revenue per facility | \$5,000-15,000 |
| Asset tag attach rate (existing customers) | 60%+ |
| Gross margin (LaaS) | 70-80% |
| Customer lifetime value | 5+ years |

### 6.4 Tag Portfolio Strategy

The protocol coexistence described in Section 4.5 enables a deliberate product tiering strategy that balances market penetration with margin optimization.

**Volume vs. Margin Mix**

| Tier | Volume Role | Margin Role | Typical Deployment Ratio |
|------|-------------|-------------|-------------------------|
| Basic (\$5-8) | High volume, land-and-expand | Low margin, drives platform adoption | 60-70% of tags |
| Standard (\$12-18) | Core business, most versatile | Healthy margin, subscription anchor | 25-35% of tags |
| Precision (\$25-40) | Premium positioning | High margin, differentiation | 5-10% of tags |

**Customer Deployment Pattern**

A typical large customer deployment follows a predictable progression:

1. **Pilot (100-500 tags):** Mixed Basic and Standard to validate accuracy requirements
2. **Rollout (5,000-20,000 tags):** Majority Basic for broad coverage, Standard for high-value zones
3. **Optimization (ongoing):** Precision tags added for specific use cases (dock doors, AGV handoff points)

### 6.5 Hardware and Software Model

The system follows an **OEM hardware with licensed software** model:

**Hardware:** Asset tags, relay nodes, reference nodes, and infrastructure nodes are manufactured by OEM partners using P1-certified reference designs. This approach:
- Leverages existing BLE/Thread/WiFi HaLow silicon ecosystems (Nordic, Silicon Labs, Qualcomm)
- Enables competitive hardware pricing through volume manufacturing
- Allows regional sourcing and customization
- Keeps P1 focused on software differentiation

**Software:** P1 licenses the embedded firmware, cloud platform, and APIs:
- Positioning Engine firmware for reference nodes and vehicle integration
- Location Cloud subscription for data aggregation, analytics, and customer API
- Device management and provisioning tools
- Mesh optimization algorithms

**Revenue Split (Typical):**
| Component | P1 Revenue | Notes |
|-----------|------------|-------|
| Hardware margin | 0-10% | Pass-through or small markup |
| Firmware license | Per device | One-time or included in subscription |
| Cloud subscription | Monthly/annual | Primary recurring revenue |
| Professional services | Project-based | Deployment, integration, custom development |

This model aligns P1's incentives with customer success: P1 earns recurring revenue from a working, reliable system rather than one-time hardware sales.

### 6.6 Competitive Moat

The LaaS model creates multiple barriers to displacement:

1. **Infrastructure investment**: Customer has P1 hardware deployed throughout facility
2. **Integration depth**: Warehouse Management System (WMS)/Enterprise Resource Planning (ERP) connected via Location Cloud API
3. **Data history**: Years of location analytics in P1 platform
4. **Switching cost**: Would require parallel deployment during transition
5. **Unified platform**: Competitors would need to match both outdoor RTK and indoor mesh
6. **Low-tier volume**: Makes rip-and-replace expensive for competitors
7. **Upgrade path**: Keeps customers expanding within the P1 ecosystem

Unlike pure-play indoor vendors (Quuppa, Zebra) or outdoor-only solutions, P1 offers **ubiquitous location**: one vendor, one API, one subscription for position anywhere.

---

## 7. Competitive Positioning

### 7.1 vs. Pure Indoor Positioning (Quuppa, Zebra, Ubisense)

These vendors require dedicated infrastructure: antenna arrays, specialized anchors, facility-specific calibration. P1's approach:

- Leverages existing GNSS gateway deployments
- Lower infrastructure cost (battery-powered relay nodes vs. wired anchors)
- Unified outdoor/indoor platform vs. separate systems
- Channel Sounding provides competitive accuracy without antenna arrays

### 7.2 vs. BLE Asset Tracking (Kontakt.io, Estimote, Asset Tracker vendors)

Pure BLE solutions lack outdoor integration and precise positioning:

- P1 provides seamless outdoor-to-indoor handoff
- GNSS-derived reference positions for all indoor zones
- Enterprise-grade API and device management
- Path to centimeter accuracy via Positioning Engine

### 7.3 vs. Cellular IoT Trackers (CalAmp, Sierra Wireless)

Cellular trackers have higher per-device cost and power consumption:

- Asset beacons: \$5-15 vs. \$50-150 for cellular
- 12-month battery life vs. weeks/months
- No cellular subscription per asset
- Better indoor coverage (BLE penetrates where cellular doesn't)

---

## 8. Implementation Roadmap

### Phase 1: Reference Design (Q1 2026)
- WiFi HaLow access point firmware for existing P1 gateways
- Reference relay node design (Nordic nRF54L15 + Thread)
- Asset beacon specification (BLE 5.x, Eddystone-EID)
- Location Cloud API extensions for asset events
- Pilot with 2-3 existing P1 fleet customers

### Phase 2: Channel Sounding Integration (Q2-Q3 2026)
- BLE 6.0 Channel Sounding support in relay nodes
- Distance-based positioning algorithms
- Zone definition and geofencing in Location Cloud
- Reference node design with integrated fiducial markers
- Vehicle camera interface specification
- Expanded pilot: warehouse + fleet integration

### Phase 3: Visual-Inertial Integration (Q3-Q4 2026)
- P1 Positioning Engine indoor aiding sources (camera, BLE CS)
- INS aiding algorithms for forklift and drone platforms
- Multi-camera vehicle configurations
- Real-time mesh refinement from vehicle observations
- WiFi HaLow infrastructure node product

### Phase 4: General Availability (Q1 2027)
- P1-certified relay node, reference node, and beacon products
- Partner ecosystem for deployment services
- Full documentation and developer resources
- Location as a Service pricing and support tiers

---

## 9. Conclusion

Point One Navigation has stated its ambition clearly: ubiquitous location, indoors and all domains. The hybrid BLE-Thread-WiFi HaLow architecture proposed here provides a practical, near-term path to that goal while generating new revenue from Location as a Service.

The key insight is that P1 already has the hard parts solved:

- Polaris RTK Network providing the geographic truth that anchors all positioning
- Enterprise-grade Location Cloud API and device management
- Trusted relationships with fleet and logistics customers
- The P1 Tags feature for customer-native integration
- P1 Positioning Engine for sensor fusion across diverse aiding sources

Adding indoor mesh networking and asset beacon support extends these strengths into new markets. Polaris provides the geographic truth; the mesh network extends that truth indoors to every pallet, container, and asset.

The opportunity is significant: every P1 fleet customer is also a potential Location as a Service customer. Every pallet on every truck, every container in every warehouse, every package in transit, all manageable through a single platform, all anchored to Polaris-grade positioning.

**P1 provides the location. Customers subscribe to ubiquitous visibility.**

---

## References

### Point One Navigation Sources

1. **TechCrunch** (November 20, 2025). "This Khosla-backed startup can track drones, trucks, and robotaxis, inch by inch." Retrieved from: https://techcrunch.com/2025/11/20/this-khosla-based-startup-can-track-drones-trucks-and-robotaxis-inch-by-inch/
   - Source for: \$35M Series C funding, \$230M valuation, Aaron Nathan quotes on indoor navigation goals, customer deployment numbers (150,000+ EV vehicles, 300,000 delivery vehicles), 10x robotics growth

2. **Point One Navigation GraphQL API Documentation**. Retrieved from: https://docs.pointonenav.com/graphql-api/
   - Source for: API patterns, `myDevices` query, `setDeviceTag` mutation, WebSocket subscriptions, device filtering

3. **Point One Navigation GitHub - Polaris Client**. Retrieved from: https://github.com/PointOneNav/polaris
   - Source for: Polaris RTK corrections service architecture, RTCM 10403 implementation, C/C++ client libraries

4. **Point One Navigation GitHub - FusionEngine Client**. Retrieved from: https://github.com/PointOneNav/fusion-engine-client
   - Source for: Positioning Engine message protocols, sensor fusion architecture

5. **Point One Navigation Developer Resources**. Retrieved from: https://pointonenav.com/resources/
   - Source for: Polaris network coverage, device management capabilities

### Bluetooth Technology Sources

6. **Bluetooth SIG** (September 2024). "Bluetooth Core Specification 6.0." Retrieved from: https://www.bluetooth.com/specifications/specs/core-specification-6-0/
   - Source for: Channel Sounding specification, Phase-Based Ranging (PBR), Round-Trip Time (RTT) security features

7. **Bluetooth SIG** (September 3, 2024). "Bluetooth SIG Introduces True Distance Awareness." Press release. Retrieved from: https://www.bluetooth.com/press/bluetooth-channel-sounding/
   - Source for: 10-centimeter accuracy claims, single-antenna capability, security features, Neville Meijers CEO quote

8. **Nordic Semiconductor**. "nRF54L15 - Ultra-low-power wireless SoC." Product documentation. Retrieved from: https://www.nordicsemi.com/Products/nRF54L15
   - Source for: BLE 6.0 Channel Sounding silicon availability, Thread support

9. **Silicon Labs**. "xG24 Wireless SoC." Product documentation. Retrieved from: https://www.silabs.com/wireless/zigbee/efr32mg24-series-2-socs
   - Source for: Multi-protocol BLE + Thread support, Channel Sounding readiness

### Thread/Matter Sources

10. **Thread Group**. "Thread 1.3 Specification." Retrieved from: https://www.threadgroup.org/
    - Source for: IPv6 mesh networking, Sleepy End Device power characteristics, Border Router functionality

11. **Connectivity Standards Alliance**. "Matter Specification." Retrieved from: https://csa-iot.org/all-solutions/matter/
    - Source for: Matter over Thread interoperability

12. **IKEA** (November 2025). "IKEA launches new smart home range with 21 Matter-compatible products." Press release. Retrieved from: https://www.ikea.com/global/en/newsroom/retail/the-new-smart-home-from-ikea-matter-compatible-251106/
    - Source for: Industry adoption momentum, 21 Matter-over-Thread devices

### WiFi HaLow Sources

13. **Wireless Broadband Alliance** (January 2024). "Wi-Fi HaLow for IoT Program." White paper. Retrieved from: https://wballiance.com/
    - Source for: WiFi HaLow commercial deployment status, use cases

14. **Morse Micro**. "Wi-Fi HaLow for IoT." Product documentation. Retrieved from: https://www.morsemicro.com/
    - Source for: WiFi HaLow SoC specifications, range and throughput capabilities

### Indoor Positioning Context

15. **Quuppa**. "Quuppa Intelligent Locating System." Technical overview. Retrieved from: https://www.quuppa.com/
    - Source for: Competitive comparison, antenna array-based RTLS architecture

16. **Zebra Technologies**. "Real-Time Location Systems (RTLS)." Product documentation. Retrieved from: https://www.zebra.com/us/en/solutions/intelligent-edge-solutions/rtls.html
    - Source for: Competitive comparison, enterprise RTLS market

### Standards

17. **RTCM Special Committee 104**. "RTCM 10403.x - Differential GNSS Services, Version 3." Retrieved from: https://www.rtcm.org/publications
    - Source for: RTK corrections data format used by Polaris network

18. **IEEE 802.15.4** (2020). "IEEE Standard for Low-Rate Wireless Networks." Retrieved from: https://en.wikipedia.org/wiki/IEEE_802.15.4
    - Source for: Thread PHY/MAC layer foundation

19. **IEEE 802.11ah** (2017). "IEEE Standard for Sub-1 GHz License-Exempt Operation." 
    - Source for: WiFi HaLow specification

---

## Glossary

**AGV (Automated Guided Vehicle):** Self-driving material handling equipment used in warehouses and factories for transporting goods without human operators.

**AprilTag:** A visual fiducial system using square black-and-white markers with encoded IDs. Designed for robust detection and precise pose estimation from camera images. Developed at University of Michigan. The "36h11" family (recommended for this application) uses a 6×6 data grid with 11-bit Hamming distance error correction, providing 587 unique tags with excellent detection reliability and minimal false positives.

**ArUco:** A visual fiducial marker system similar to AprilTag, developed by the University of Córdoba. ArUco dictionaries provide predefined sets of markers optimized for different use cases—smaller dictionaries (e.g., 4×4_50) offer faster detection, while larger dictionaries (e.g., 6×6_250) provide more unique IDs and better error correction.

**Channel Sounding:** A Bluetooth 6.0 feature that measures distance between devices by analyzing signal characteristics across multiple frequency channels. Achieves 10-centimeter accuracy using phase-based ranging.

**Covariance Matrix:** A mathematical representation of uncertainty and correlations between estimated variables. In positioning, it quantifies how confident the system is about each coordinate and how errors in one dimension relate to errors in others.

**CS Reflector:** A Bluetooth 6.0 device role in Channel Sounding where the device responds to ranging requests from an initiator. Asset tags typically operate as reflectors, enabling relay nodes (initiators) to measure distance to the tag.

**Dead Reckoning:** Position estimation by integrating velocity and heading measurements from motion sensors. Useful for short-term position continuity but accumulates drift over time without external corrections.

**Eddystone-EID (Ephemeral Identifier):** A Google-developed beacon protocol that transmits encrypted, rotating identifiers. Prevents unauthorized tracking while allowing authorized systems to resolve the beacon's true identity.

**EKF (Extended Kalman Filter):** A recursive algorithm for estimating the state of a system from noisy measurements. Extends the classic Kalman filter to handle nonlinear relationships between measurements and state variables.

**Factor Graph:** A graphical model representing the relationships between variables and constraints. In positioning, nodes represent device positions and edges represent distance measurements, enabling globally consistent solutions.

**Fiducial Marker:** A visual pattern placed in the environment that can be detected by cameras to provide position and orientation reference. Common types include AprilTags, ArUco markers, and QR codes.

**GraphQL:** A query language and runtime for APIs developed by Facebook. Unlike REST APIs with fixed endpoints, GraphQL allows clients to request exactly the data they need in a single query. P1's Location Cloud uses GraphQL for device management, position queries, and real-time subscriptions.

**IMU (Inertial Measurement Unit):** A sensor package containing accelerometers and gyroscopes that measure acceleration and rotation. Used for dead reckoning and sensor fusion in navigation systems.

**Infrastructure Node:** A mains-powered device in the positioning mesh that aggregates data from multiple relay nodes using high-bandwidth WiFi HaLow connectivity and forwards to P1 gateways.

**INS (Inertial Navigation System):** A navigation system that computes position by integrating acceleration and rotation measurements from an IMU, typically aided by external observations (GNSS, visual landmarks, radio ranging) to correct drift.

**Innovation Gating:** An outlier rejection technique that discards measurements whose difference from the predicted value exceeds a statistical threshold based on expected uncertainty.

**IPv6 (Internet Protocol version 6):** The latest version of the Internet Protocol, providing a vastly expanded address space that allows every device to have a unique, routable address.

**Location as a Service (LaaS):** A subscription business model where customers pay for continuous, accurate position data rather than purchasing hardware and software separately. P1 provides the infrastructure, maintenance, and platform; customers consume location.

**Mahalanobis Distance:** A statistical measure of distance that accounts for correlations and variances in the data. Used to determine whether a measurement is consistent with an expected distribution, enabling outlier detection.

**Multipath:** A radio propagation phenomenon where signals reflect off surfaces and arrive at the receiver via multiple paths. Causes range measurement errors in indoor environments.

**NLOS (Non-Line-of-Sight):** A condition where the direct path between transmitter and receiver is obstructed, forcing signals to travel via reflections or diffraction. Degrades ranging accuracy.

**Particle Filter:** A Sequential Monte Carlo method that represents probability distributions using weighted samples (particles). Handles non-Gaussian noise and multimodal hypotheses better than Kalman filters.

**Polaris:** Point One Navigation's global RTK corrections network, delivering centimeter-accurate GNSS positioning via 2,000+ professionally managed base stations across North America, Europe, and Asia. Corrections are streamed to devices over cellular or internet connections.

**Phase-Based Ranging (PBR):** A distance measurement technique that calculates range from the phase difference of signals transmitted across multiple frequencies.

**Reference Node:** A combined fiducial marker and BLE beacon that participates in the self-locating mesh and provides visual landmarks for camera-equipped vehicles.

**RSSI (Received Signal Strength Indicator):** A measurement of received signal power, commonly used for rough proximity estimation. Less accurate than Channel Sounding but simpler to implement.

**RTK (Real-Time Kinematic):** A satellite navigation technique that achieves centimeter-level accuracy by using carrier phase measurements and real-time corrections from a reference station or network.

**RTLS (Real-Time Location System):** Infrastructure for automatically tracking the location of assets or personnel within a defined area, typically using radio frequency technologies.

**Thread:** An IPv6-based mesh networking protocol designed for low-power IoT devices. Provides self-healing connectivity and supports devices that sleep most of the time to conserve battery.

**Thread Border Router:** A device that bridges a Thread mesh network to external IP networks such as Wi-Fi or Ethernet, enabling Thread devices to communicate with the broader internet.

**Trilateration:** A positioning technique that determines location by measuring distances from three or more reference points with known positions. The intersection of the resulting spheres (or circles in 2D) yields the target position.

**ULD (Unit Load Device):** A standardized container or pallet used for air cargo transport, designed to fit aircraft cargo holds efficiently.

**Visual-Inertial Odometry (VIO):** A technique that fuses camera images and IMU data to estimate motion and position. Related to but distinct from full visual-inertial navigation with external landmark aiding.

**WiFi HaLow (802.11ah):** A WiFi standard operating in sub-1 GHz frequencies, designed for IoT applications requiring longer range (up to 1km), better obstacle penetration, and support for thousands of devices per access point. Provides higher bandwidth than Thread while maintaining low power operation.

**WPA3 (Wi-Fi Protected Access 3):** The latest WiFi security protocol, providing stronger encryption, protection against offline dictionary attacks, and simplified security for IoT devices. Required for enterprise-grade wireless deployments.

**WMS (Warehouse Management System):** Software that controls and optimizes warehouse operations including inventory tracking, order fulfillment, and storage optimization.

---

## Appendix A: Mathematical Details

This appendix provides the mathematical foundations for the sensor fusion algorithms described in Section 4.4 and 4.6.

### A.1 Extended Kalman Filter Equations

The EKF maintains a state vector and covariance matrix:

```
State Vector: x = [lat, lon, alt]ᵀ
Covariance Matrix: P (3×3 uncertainty estimate)
```

**Predict Step**

For static relay nodes, the prediction step simply propagates the previous estimate with added process noise to account for potential drift:

```
x̂ₖ|ₖ₋₁ = x̂ₖ₋₁            (position unchanged for static relay)
Pₖ|ₖ₋₁ = Pₖ₋₁ + Q        (add process noise covariance)
```

Where Q is typically near-zero for fixed relays but may be increased if relay movement is suspected.

**Update Step**

When a position donation arrives from a P1 device:

```
Measurement:      z = P1_position + channel_sounding_offset
Innovation:       y = z - x̂ₖ|ₖ₋₁
Innovation Cov:   S = Pₖ|ₖ₋₁ + R
Kalman Gain:      K = Pₖ|ₖ₋₁ S⁻¹
Updated State:    x̂ₖ = x̂ₖ|ₖ₋₁ + K·y
Updated Cov:      Pₖ = (I - K)Pₖ|ₖ₋₁
```

Where R is the measurement noise covariance, derived from the combined uncertainty of the P1 device's RTK position and the Channel Sounding range measurement.

**Measurement Noise Covariance**

The R matrix combines uncertainties from multiple sources:

```
R = R_rtk + R_cs + R_multipath

Where:
  R_rtk       = RTK position uncertainty (typically ±0.02m, from P1 device)
  R_cs        = Channel Sounding ranging uncertainty (typically ±0.1m)
  R_multipath = Environment-dependent multipath error (0.1-0.5m indoor)
```

### A.2 Why EKF is Ideal for Relay Position Estimation

| Challenge | EKF Solution |
|-----------|--------------|
| Noisy range measurements | Measurement noise covariance (R) weights observations appropriately |
| Varying P1 device accuracy | R adapts based on reported RTK accuracy (±2cm vs ±10cm) |
| Multipath/NLOS outliers | Innovation gating rejects measurements where \|y\| > 3√S |
| Unknown initial position | Large initial P (e.g., 1000m²) allows rapid convergence |
| Static relay assumption | Q ≈ 0 for fixed relays; increase Q if movement detected |

### A.3 Particle Filter

The Particle Filter represents the position probability distribution using N weighted samples:

```
Particles: {x⁽ⁱ⁾, w⁽ⁱ⁾} for i = 1...N

For each measurement z:
1. PREDICT:  x⁽ⁱ⁾ₖ|ₖ₋₁ = f(x⁽ⁱ⁾ₖ₋₁) + noise
2. UPDATE:   w⁽ⁱ⁾ ∝ p(z | x⁽ⁱ⁾ₖ|ₖ₋₁)
3. RESAMPLE: Draw N particles proportional to weights

Estimate: x̂ = Σᵢ w⁽ⁱ⁾ x⁽ⁱ⁾
```

**Advantages over EKF:**
- Handles non-Gaussian noise (common in indoor RF)
- Represents multimodal distributions (relay could be in multiple possible locations)
- No linearization required

**Disadvantages:**
- Computationally expensive (N = 100-1000 particles typical)
- May require more memory than available on low-power relay Microcontroller Units (MCUs)

### A.4 Factor Graph Optimization

Models the relay mesh as a graph:
- **Variable nodes:** Relay positions (x₁, x₂, ... xₙ)
- **Factor nodes:** Constraints from measurements

```
Minimize: Σᵢⱼ ||d_measured(i,j) - ||xᵢ - xⱼ|| ||² / σᵢⱼ²

Subject to: Anchor constraints from P1 device observations
```

Solved iteratively using Gauss-Newton or Levenberg-Marquardt optimization.

**Advantages:**
- Globally consistent solution across entire mesh
- Naturally incorporates relay-to-relay ranging
- Can detect and correct for moved relays

**Implementation:**
- Typically runs in Location Cloud (not on relay MCU)
- Executed periodically (e.g., hourly) or when topology changes
- Results pushed back to relay nodes

### A.5 Mahalanobis Distance for Outlier Rejection

The Mahalanobis distance measures how far a measurement is from the expected value, normalized by uncertainty:

```
d_M = √(yᵀ S⁻¹ y)

Where:
  y = innovation (measurement - prediction)
  S = innovation covariance
```

Measurements with d_M > threshold (typically 3.0) are rejected as outliers. This approach automatically adapts to the current uncertainty: when position is poorly known, more measurements are accepted; as confidence increases, outliers are more readily rejected.

### A.6 Trilateration Mathematics

Given distances d₁, d₂, d₃ from relay nodes at known positions (x₁,y₁), (x₂,y₂), (x₃,y₃):

```
(x - x₁)² + (y - y₁)² = d₁²
(x - x₂)² + (y - y₂)² = d₂²
(x - x₃)² + (y - y₃)² = d₃²
```

Subtracting equations to linearize:

```
2(x₂-x₁)x + 2(y₂-y₁)y = d₁² - d₂² + x₂² - x₁² + y₂² - y₁²
2(x₃-x₁)x + 2(y₃-y₁)y = d₁² - d₃² + x₃² - x₁² + y₃² - y₁²
```

Solve the resulting 2×2 linear system for (x, y).

With more than three relays, use weighted least squares to find the position that minimizes total squared error, with weights inversely proportional to measurement uncertainty.

### A.7 Visual Observation Model

When a camera detects a fiducial marker, the observation provides bearing, elevation, and range information that can be fused with the vehicle's state estimate.

**State Vector (Vehicle)**

```
x = [px, py, pz, vx, vy, vz, φ, θ, ψ, bax, bay, baz, bgx, bgy, bgz]ᵀ

Where:
  p = position (3D)
  v = velocity (3D)
  φ, θ, ψ = attitude (roll, pitch, yaw)
  ba = accelerometer biases (3D)
  bg = gyroscope biases (3D)
```

**Measurement Model**

Given known fiducial position (Xf, Yf, Zf) and current vehicle state estimate:

```
Predicted bearing:    β̂ = atan2(Yf - py, Xf - px) - ψ
Predicted elevation:  ε̂ = atan2(Zf - pz, √((Xf-px)² + (Yf-py)²))
Predicted range:      r̂ = √((Xf-px)² + (Yf-py)² + (Zf-pz)²)
```

**Measurement Jacobian**

The Jacobian H relates changes in state to changes in predicted measurement:

```
H = ∂h/∂x = [∂β̂/∂p, 0, ∂β̂/∂ψ, 0, 0;
             ∂ε̂/∂p, 0, 0, 0, 0;
             ∂r̂/∂p, 0, 0, 0, 0]
```

**Measurement Noise**

```
R_visual = diag(σ²_bearing, σ²_elevation, σ²_range)

Typical values:
  σ_bearing   = 0.5° = 0.0087 rad
  σ_elevation = 0.5° = 0.0087 rad
  σ_range     = 0.05 × range (5% of distance)
```

**Fusion with BLE CS**

When both visual and BLE CS observations are available for the same reference node, they provide complementary information:

```
z_combined = [β_camera, ε_camera, r_camera, r_BLE]ᵀ

R_combined = diag(σ²_β, σ²_ε, σ²_r_camera, σ²_r_BLE)
```

The BLE CS range typically has better accuracy than the camera-derived range (especially at distance), while the camera provides superior angular information.

---

## About the Author

**Richard W. Lourette** is the founder and principal consultant at RL Tech Solutions LLC, bringing 30+ years of experience in embedded systems architecture across aerospace, defense, and industrial IoT.

**Relevant Experience:**

**Panasonic Industrial IoT Division (Engineering Group Manager, 2021-2022)**
- Managed cross-functional teams spanning RF engineering, mesh networking, antenna development, and embedded firmware
- Directed R&D for industrial IoT devices with RESTful API integration
- Resolved critical RF protocol issues for 2,000+ device deployments
- Evaluated indoor positioning technologies including Quuppa-based RTLS systems

**Topcon Positioning Systems (Senior Embedded Software Consultant, 2023-2025)**
- Architected Linux C++ subsystems for next-generation GNSS receivers
- Deep understanding of RTK positioning, carrier phase measurements, and precision navigation
- Delivered 150,000+ lines of production embedded, unit test, and system test code

**L3Harris Aerospace (Chief Engineer Consultant, 2022-2023)**
- Spacecraft payload systems integrating radiation-hardened MCUs via SpaceWire
- NASA Core Flight System (cFS) architecture on RTEMs RTOS

Richard is a named inventor on 20 U.S. patents and has held DoD Top Secret/SCI clearances. His background uniquely combines GNSS/positioning expertise with industrial IoT system architecture, directly applicable to extending P1's platform into indoor and asset tracking domains.

---

**Document Version:** 2.8  
**Date:** December 2025

© 2025 Richard W. Lourette. All rights reserved.