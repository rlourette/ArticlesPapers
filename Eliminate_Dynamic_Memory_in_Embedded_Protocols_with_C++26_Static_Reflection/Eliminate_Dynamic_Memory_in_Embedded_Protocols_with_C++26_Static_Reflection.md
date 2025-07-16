# Eliminating Dynamic Memory in Embedded Protocols with C++26 Static Reflection: A CoAP Case Study

*By Richard Lourette*  
*Published: July 2025*

![CoAP and C++26 illustration showing a modern poolside setting with CoAP protocol displayed on a large screen and C++26 text reflected in the water, representing the elegant combination of constrained application protocols with modern C++ reflection capabilities](CoAP_C++_reflection.png)

## Overview

With the release of **C++26**, embedded developers have access to powerful compile-time capabilities like standardized **static reflection** (`std::meta`) and improved `consteval`/`constexpr` features. These advances unlock a new level of **safety, determinism, and clarity**, which is particularly useful in safety-critical systems where **dynamic memory is forbidden**.

This article demonstrates how to use C++26 to implement the [Constrained Application Protocol (CoAP)](https://datatracker.ietf.org/doc/html/rfc7252) on embedded systems **without any dynamic memory allocation**, using **compile-time code generation** to handle message serialization, endpoint registration, and secure payload exchange with **DTLS (Datagram Transport Layer Security)**.

## What is CoAP?

**CoAP** is a lightweight RESTful protocol designed specifically for **constrained embedded devices** like microcontrollers or wireless sensors. It resembles HTTP in its request/response model (GET, POST, PUT, DELETE) but uses **UDP** instead of TCP to reduce overhead. This makes it ideal for:

- Battery-powered IoT devices
- Sensor networks (e.g., LoRaWAN, 6LoWPAN)
- Real-time or bandwidth-constrained applications

CoAP supports:

- Multicast messaging
- Observing resources (`Observe`)
- Confirmable/non-confirmable delivery
- Secure communication via **DTLS**

For a full specification, see [RFC 7252](https://datatracker.ietf.org/doc/html/rfc7252).

## Why C++26?

Historically, embedded developers have used either C or a subset of older C++ (C++03/11) to avoid complex runtime behavior. **C++26** changes this paradigm with:

- **`std::meta`**: Standardized static reflection for compile-time introspection
- **`consteval`**: Compile-time evaluation for code generation
- **`constexpr`**: Enables constant initialization of complex data structures
- **Zero-overhead abstractions**: Type safety without runtime cost

These features enable us to **generate optimized CoAP protocol logic at compile time**, achieving both safety and performance without sacrificing expressiveness.

## System Requirements

This implementation targets embedded systems with the following characteristics:

**Hardware Platform:**

- Microcontroller (STM32, Nordic nRF52, ESP32, etc.)
- 32KB+ RAM, 256KB+ Flash
- UDP networking capability

**Software Stack:**

- Bare-metal or lightweight RTOS (Zephyr, FreeRTOS)
- CoAP stack with DTLS support ([TinyDTLS](https://github.com/eclipse/tinydtls), [mbedTLS](https://github.com/Mbed-TLS/mbedtls))
- [ETL (Embedded Template Library)](https://www.etlcpp.com/) for static containers
- C++26-compatible compiler (GCC 15+, Clang 19+ with reflection support)

**Key Constraints:**

- No dynamic memory allocation
- Deterministic timing requirements
- Memory-constrained environment
- Safety-critical compliance (optional)

## Example: CoAP Request/Response with Static Reflection

We define a request and response pair using strongly typed message structs:

```cpp
struct [[meta::reflect]] GetTemperatureRequest {
    uint16_t sensor_id;
};

struct [[meta::reflect]] GetTemperatureResponse {
    float temperature_celsius;
    uint64_t timestamp;
};
```

We can now use **C++26 static reflection** to iterate over each field **at compile time** and generate serialization logic.

### Compile-Time Serialization

```cpp
template <typename T>
constexpr etl::vector<uint8_t, MaxPayloadSize> serialize_to_coap(const T& msg) {
    etl::vector<uint8_t, MaxPayloadSize> buffer;

    for (auto member : std::meta::members_of(reflexpr(T))) {
        using MemberType = std::remove_cvref_t<decltype(msg.*std::meta::get_pointer(member))>;
        const auto& field = msg.*std::meta::get_pointer(member);

        if constexpr (std::is_same_v<MemberType, uint16_t>) {
            buffer.push_back(static_cast<uint8_t>(field >> 8));
            buffer.push_back(static_cast<uint8_t>(field & 0xFF));
        } else if constexpr (std::is_same_v<MemberType, float>) {
            auto bytes = to_bytes(field); // constexpr helper
            buffer.insert(buffer.end(), bytes.begin(), bytes.end());
        } else if constexpr (std::is_same_v<MemberType, uint64_t>) {
            for (int i = 7; i >= 0; --i)
                buffer.push_back(static_cast<uint8_t>((field >> (8 * i)) & 0xFF));
        } else {
            static_assert(std::is_trivially_copyable_v<MemberType>,
                "Unsupported field type in CoAP message");
        }
    }

    return buffer;
}
```

This function uses fixed-size buffers (`etl::vector`) and **no dynamic memory allocation**. The serialization logic is generated at compile time, ensuring deterministic layout and timing for safety-critical applications. 

**Note:** Multi-byte integer fields are serialized in network byte order (big-endian), as required by CoAP and most network protocols.

## 🔐 Secure Payloads with DTLS

CoAP uses **DTLS** to secure messages, similar to how HTTPS secures HTTP. DTLS adds confidentiality, integrity, and authentication over **UDP**, which is essential in untrusted or wireless environments.

### Example DTLS Use with Serialized Payload

```cpp
void send_secure_response(const GetTemperatureResponse& msg) {
    auto payload = serialize_to_coap(msg);

    dtls_encrypt_and_send(payload.data(), payload.size(), remote_address, remote_port);
}
```

This assumes your CoAP stack is integrated with a DTLS library like:

- [TinyDTLS](https://github.com/eclipse/tinydtls)
- [mbedTLS](https://github.com/Mbed-TLS/mbedtls)
- [wolfSSL](https://www.wolfssl.com/)

### C++26 and Security

C++26's static reflection enables **compile-time security policies** with zero runtime overhead. You can tag sensitive fields and enforce access controls automatically:

```cpp
// Security annotation attributes
namespace security {
    struct sensitive {};
    struct encrypted {};
    struct public_only {};
}

struct [[meta::reflect]] SecureSensorMessage {
    [[sensitive, encrypted]] uint16_t sensor_id;
    [[public_only]] float reading;
    [[sensitive]] uint32_t device_key_hash;
    uint64_t timestamp;
};
```

The reflection system can then automatically handle encryption based on these annotations, ensuring sensitive data is never transmitted in plaintext by accident.

*For detailed security implementation examples, see the Advanced Security Features section below.*

## Practical Implementation Example

Let's build a complete temperature sensor that demonstrates the concepts above:

```cpp
#include <etl/vector.h>
#include <meta>

// Message definitions
struct [[meta::reflect]] TemperatureSensorRequest {
    uint16_t sensor_id;
    uint8_t sampling_rate; // Hz
};

struct [[meta::reflect]] TemperatureSensorResponse {
    float temperature_celsius;
    float humidity_percent;
    uint64_t timestamp_ms;
    uint8_t battery_level; // 0-100%
};

// CoAP endpoint implementation
class TemperatureSensorEndpoint {
public:
    static constexpr auto URI_PATH = "/sensors/temperature";
    
    static auto handle_request(const TemperatureSensorRequest& req) {
        // Read sensor data (implementation-specific)
        auto sensor_data = read_sensor(req.sensor_id);
        
        TemperatureSensorResponse response{
            .temperature_celsius = sensor_data.temperature,
            .humidity_percent = sensor_data.humidity,
            .timestamp_ms = get_system_time_ms(),
            .battery_level = get_battery_level()
        };
        
        return response;
    }
};

// Compile-time endpoint registration
template<typename Endpoint>
constexpr auto register_endpoint() {
    return CoAPEndpoint{
        .path = Endpoint::URI_PATH,
        .handler = &Endpoint::handle_request,
        .request_type = std::meta::type_of(^typename Endpoint::RequestType),
        .response_type = std::meta::type_of(^typename Endpoint::ResponseType)
    };
}

// Usage in main application
int main() {
    constexpr auto endpoints = std::array{
        register_endpoint<TemperatureSensorEndpoint>()
        // Add more endpoints here...
    };
    
    CoAPServer server(endpoints);
    server.start();
    
    while (true) {
        server.process_requests();
        // Handle other system tasks...
    }
}
```

This example demonstrates:

- **Type-safe message definitions** with automatic serialization
- **Compile-time endpoint registration** using reflection
- **Zero-allocation server architecture** using static containers
- **Deterministic behavior** suitable for real-time systems

## Benefits for Safety-Critical Systems

| Feature                          | Benefit                                                                 |
|----------------------------------|-------------------------------------------------------------------------|
| `std::meta` static reflection    | Eliminates boilerplate; enforces message format consistency             |
| No dynamic memory                | Suitable for DO-178C, ISO 26262, and real-time use cases                |
| Compile-time serialization       | Deterministic behavior, improves WCET analysis                          |
| Strong typing                    | Compile-time checks for field validity and completeness                 |
| DTLS security with compile-time layout | Prevents buffer overflows or encoding errors in secure contexts     |
| **Field-level security annotations** | **Zero-runtime-cost access control and encryption policies**        |
| **Compile-time audit trail**     | **Automatic security compliance verification and logging**              |
| **Role-based access control**    | **Compile-time enforcement of data classification levels**              |
| **Selective encryption**         | **Automatic encryption of sensitive fields based on annotations**       |

## Future Extensions Using C++26

### ✅ Auto-register message types to CoAP endpoints

Use `meta::type_name()` or `[[coap_path("/myuri")]]` attributes to generate endpoint tables at compile time.

```cpp
[[coap_path("/temperature")]]
struct GetTemperatureRequest { ... };

// Dispatcher
static constexpr auto uri = get_attribute_or_type_name<GetTemperatureRequest>();
coap_server.register_handler(uri, handler_for<GetTemperatureRequest>);
```

### ✅ Compile-Time Fuzz Testing Harness

With static reflection:

- Automatically generate field values (min, max, overflow, invalid)
- Ensure serialization code handles edge cases
- Fully `constexpr` test vector generation

```cpp
template <typename T>
constexpr auto fuzz_cases = generate_fuzz_cases<T>();
```

### ✅ Static Checks for Layout and Safety

Ensure messages are:

- Byte-aligned
- Free of padding
- Size-bounded for transmission buffers

```cpp
static_assert(validate_layout<SomeCoapMessage>(), "Message layout is unsafe!");
```

## Security Compliance for Safety-Critical Systems

The compile-time security annotations and reflection-based access controls provide strong guarantees for safety-critical systems that must meet strict certification requirements:

### DO-178C and Common Criteria Compliance

- **Deterministic Security**: All security decisions made at compile time eliminate runtime variability
- **Formal Verification**: Security policies can be mathematically proven correct through static analysis
- **No Side Channels**: Zero-runtime-cost security prevents timing-based attacks
- **Audit Trail**: Complete compile-time documentation of all security-relevant decisions

### IEC 62443 Industrial Security Standards

The annotation-based approach directly supports industrial cybersecurity requirements:

```cpp
// IEC 62443 security level annotations
enum class IEC62443_SL { SL1, SL2, SL3, SL4 };

struct [[meta::reflect]] IndustrialControlMessage {
    [[security_level<IEC62443_SL::SL3>]] uint32_t control_command;
    [[security_level<IEC62443_SL::SL2>]] float sensor_reading;
    [[security_level<IEC62443_SL::SL4>]] uint64_t safety_interlock;
};
```

### NIST Cybersecurity Framework Integration

The compile-time security model maps directly to NIST CSF functions:

- **Identify**: Automatic discovery of sensitive data through reflection
- **Protect**: Compile-time encryption and access control enforcement  
- **Detect**: Built-in audit logging of security-relevant operations
- **Respond**: Immediate compile-time failure for policy violations
- **Recover**: Deterministic fallback behaviors encoded in security policies

## Advanced Security Features

This section provides detailed implementation examples of the security concepts introduced earlier.

### Compile-Time Security Policy Enforcement

```cpp
template <typename T>
constexpr auto get_sensitive_fields() {
    std::vector<std::string_view> sensitive_fields;
    for (auto member : std::meta::members_of(reflexpr(T))) {
        if (std::meta::has_attribute(member, reflexpr(security::sensitive))) {
            sensitive_fields.push_back(std::meta::name_of(member));
        }
    }
    return sensitive_fields;
}

// Compile-time validation that sensitive fields are handled
template <typename T>
constexpr bool validate_security_policy() {
    constexpr auto sensitive = get_sensitive_fields<T>();
    static_assert(!sensitive.empty() || has_no_sensitive_data<T>(),
                  "Message type must declare security policy");
    return true;
}
```

### Selective Encryption Based on Annotations

```cpp
template <typename T>
constexpr etl::vector<uint8_t, MaxPayloadSize> serialize_with_security(const T& msg) {
    etl::vector<uint8_t, MaxPayloadSize> buffer;
    etl::vector<uint8_t, MaxPayloadSize> encrypted_buffer;

    for (auto member : std::meta::members_of(reflexpr(T))) {
        using MemberType = std::remove_cvref_t<decltype(msg.*std::meta::get_pointer(member))>;
        const auto& field = msg.*std::meta::get_pointer(member);
        
        // Serialize field using same logic as main serialization function
        etl::vector<uint8_t, 16> field_bytes;
        if constexpr (std::is_same_v<MemberType, uint16_t>) {
            field_bytes.push_back(static_cast<uint8_t>(field >> 8));
            field_bytes.push_back(static_cast<uint8_t>(field & 0xFF));
        } else if constexpr (std::is_same_v<MemberType, float>) {
            auto bytes = to_bytes(field); // constexpr helper
            field_bytes.insert(field_bytes.end(), bytes.begin(), bytes.end());
        } else if constexpr (std::is_same_v<MemberType, uint32_t>) {
            for (int i = 3; i >= 0; --i)
                field_bytes.push_back(static_cast<uint8_t>((field >> (8 * i)) & 0xFF));
        } else if constexpr (std::is_same_v<MemberType, uint64_t>) {
            for (int i = 7; i >= 0; --i)
                field_bytes.push_back(static_cast<uint8_t>((field >> (8 * i)) & 0xFF));
        }

        // Route field based on security annotations
        if (std::meta::has_attribute(member, reflexpr(security::encrypted))) {
            // Add to encrypted section
            encrypted_buffer.insert(encrypted_buffer.end(),
                                  field_bytes.begin(), field_bytes.end());
        } else if (std::meta::has_attribute(member, reflexpr(security::public_only))) {
            // Add to plaintext section
            buffer.insert(buffer.end(), field_bytes.begin(), field_bytes.end());
        } else if (std::meta::has_attribute(member, reflexpr(security::sensitive))) {
            static_assert(std::meta::has_attribute(member, reflexpr(security::encrypted)),
                         "Sensitive fields must be encrypted");
        } else {
            // Default: add to plaintext section
            buffer.insert(buffer.end(), field_bytes.begin(), field_bytes.end());
        }
    }

    // Encrypt sensitive section with DTLS
    if (!encrypted_buffer.empty()) {
        auto encrypted_payload = dtls_encrypt(encrypted_buffer);
        buffer.insert(buffer.end(), encrypted_payload.begin(), encrypted_payload.end());
    }

    return buffer;
}
```

### Role-Based Access Control

```cpp
enum class SecurityLevel { PUBLIC, INTERNAL, RESTRICTED, SECRET };

template <SecurityLevel level>
struct access_control {};

struct [[meta::reflect]] ClassifiedSensorData {
    [[access_control<SecurityLevel::PUBLIC>]] float temperature;
    [[access_control<SecurityLevel::INTERNAL>]] uint16_t device_id;
    [[access_control<SecurityLevel::RESTRICTED>]] uint32_t session_key;
    [[access_control<SecurityLevel::SECRET>]] uint64_t master_key_hash;
};

template <SecurityLevel user_level, typename T>
constexpr auto filter_by_access_level(const T& data) {
    std::vector<std::string_view> allowed_fields;
    for (auto member : std::meta::members_of(reflexpr(T))) {
        if (std::meta::get_attribute(member, reflexpr(access_control)) <= user_level) {
            allowed_fields.push_back(std::meta::name_of(member));
        }
    }
    return allowed_fields;
}

// Usage: Only PUBLIC and INTERNAL fields will be serialized
auto filtered = filter_by_access_level<SecurityLevel::INTERNAL>(sensor_data);
```

### Zero-Runtime-Cost Security Validation

```cpp
template <typename T>
constexpr bool security_policy_check() {
    // Verify all sensitive fields are properly annotated
    static_assert(all_sensitive_fields_encrypted<T>(),
                  "All sensitive fields must be encrypted");
    
    // Verify no plaintext leakage of sensitive data
    static_assert(no_sensitive_in_public_fields<T>(),
                  "Sensitive data cannot be in public fields");
    
    // Verify encryption key management
    static_assert(has_proper_key_management<T>(),
                  "Message type requires proper key management");
    
    return true;
}

// Compile-time validation - fails compilation if policies are violated
static_assert(security_policy_check<SecureSensorMessage>());
```

This approach enables **defense-in-depth** at the language level, ensuring security policies are impossible to bypass or forget, while maintaining the zero-overhead principles essential for embedded systems.

## Conclusion

C++26's static reflection represents a paradigm shift for embedded systems development. By moving protocol logic, security policies, and data validation to compile time, we achieve:

**Technical Benefits:**

- **Zero dynamic allocation**: All memory usage is statically determined
- **Deterministic behavior**: Critical for real-time and safety-critical systems  
- **Type safety**: Compile-time verification prevents entire classes of bugs
- **Performance**: Generated code is optimized and has no runtime reflection overhead

**Development Benefits:**

- **Reduced boilerplate**: Automatic serialization and endpoint registration
- **Maintainability**: Security policies are declarative and centralized
- **Compliance ready**: Built-in support for safety and security standards

**Real-world Impact:**

Whether you're building IoT sensor nodes, industrial control systems, or avionics modules, C++26 enables secure, efficient communication protocols without sacrificing the determinism and resource constraints that embedded systems demand.

The combination of **CoAP**, **DTLS**, and **C++26 static reflection** provides a powerful foundation for the next generation of connected embedded devices, making them both highly capable and provably safe.

## References

- [RFC 7252 – Constrained Application Protocol (CoAP)](https://datatracker.ietf.org/doc/html/rfc7252)  
- [RFC 9147 – Datagram Transport Layer Security (DTLS) 1.3](https://datatracker.ietf.org/doc/html/rfc9147)  
- [C++26 Static Reflection — P2996R1](https://isocpp.org/files/papers/P2996R1.html)  
- [ETL: Embedded Template Library](https://www.etlcpp.com/)  
- [TinyDTLS GitHub](https://github.com/eclipse/tinydtls)  
- [ISO 26262 – Functional Safety](https://www.iso.org/standard/68383.html)

---

## About the Author

**Richard Lourette** is a Principal Embedded Software Engineer and Architect specializing in embedded systems, highly reliable, safety-critical software, and modern C++ development. Connect with him on [LinkedIn](https://www.linkedin.com/in/richard-lourette-8569b3/) for more insights on embedded development and C++ innovations.

## Copyright & Usage

© 2025 Richard Lourette. This work is licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). You are free to share and adapt this material for any purpose, even commercially, provided you give appropriate credit to the author.

## Keywords

#CPP26 #EmbeddedSystems #StaticReflection #CoAP #EmbeddedCPlusPlus #SafetyCritical #IoT #DTLS #CompileTime #ZeroOverhead #Microcontrollers #RealTime #ISO26262 #FunctionalSafety #EmbeddedSecurity #ModernCPlusPlus #ConstrainedDevices #NetworkProtocols #TypeSafety #EmbeddedDevelopment
