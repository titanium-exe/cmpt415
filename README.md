**Course**: CMPT 415  
**Date**: March 30, 2025  
**Author**: Ekamleen  

---

## Experiment 1 [**Failed**]

- **User Intent**: Parse Ethernet and IPv4 headers and forward packets unchanged
- **Prompt Generator**:  
    ```python
    detailed_prompt = (
        f"{high_level_prompt}. "
        "Write valid, complete P4_16 code for the BMv2 `v1model` architecture that compiles with `p4c-bm2-ss`. "
        "Include all required blocks: headers, metadata, parser, ingress, egress, deparser, VerifyChecksum, ComputeChecksum. "
        "Define an empty `struct metadata {}`. "
        "End with `V1Switch(...) main;` using all six components exactly:\n"
        "`V1Switch(MyParser(), VerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;`"
    )
    ```

- **Observation**:  
  In the fifth iteration, one of at least four errors was resolved. Despite an explicit prompt provided initially, the LLM only improved the code after the fifth iteration, incorporating feedback from `p4c-bm2-ss`. The feedback consisted of the same error repeated five times, indicating persistent issues.

- **Improvement**:  
    ```p4
    V1Switch(
        MyParser(),
        MyVerifyChecksum(),
        MyIngress(),
        MyEgress(),
        MyComputeChecksum(),
        MyDeparser()
    ) main;
    ```


 [Comparison of 1st and 5th Outputs](experiment1-failed/1-and-5-summary.txt)


---

## Experiment 2 [**Success**]

- **Iteration No**: 5 
- **User Intent**: Parse Ethernet headers and forward packets unchanged
- **Prompt Generator**:  
  ```python
  detailed_prompt = (
        f"{high_level_prompt}. Generate valid P4_16 code that compiles successfully using p4c-bm2-ss. "
        "The code should target a simple switch architecture (e.g., v1model) and include basic packet parsing, "
        "match-action tables, and egress processing. Ensure the code is complete with necessary headers, parsers, "
        "and control blocks."
    )
    ```
- **Common Errors**:

 [Comparison of 1st and 5th Outputs](experiment2-success/1_5_Output.txt)


---

## Experiment 3 [**Success**]

- **Iteration No**: 3 
- **User Intent**: drop all tcp packets with destination port 80 
- **Prompt Generator**:  
   ```python
  detailed_prompt = (
        f"{high_level_prompt}. "
        "Generate valid, complete P4_16 code that compiles with `p4c-bm2-ss` for the BMv2 `v1model` architecture. "
        "The code must define:\n"
        "- Ethernet, IPv4, and TCP headers (`ethernet_t`, `ipv4_t`, `tcp_t`).\n"
        "- A `headers` struct with exactly: `ethernet_t ethernet; ipv4_t ipv4; tcp_t tcp;`\n"
        "- An empty `struct metadata {}`.\n"
        "- A parser named `MyParser` with correct signature and transitions for Ethernet → IPv4 → TCP.\n"
        "- Control blocks named: `MyIngress`, `MyEgress`, `MyComputeChecksum`, `MyDeparser` (can be empty).\n"
        "- Do **not** redefine `VerifyChecksum`; instead, use BMv2's built-in: `VerifyChecksum<headers, metadata>()`.\n"
        "- To drop packets, set `standard_metadata.egress_spec = 0;`. Do **not** use `drop()` unless defined.\n"
        "End the program with exactly:\n"
        "`V1Switch(MyParser(), VerifyChecksum<headers, metadata>(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;`"
    )
    ```
- **Common Errors**:

 [Comparison of 1st and 3rd Outputs](experiment3-success/1_3_output.txt)

---

## Experiment 4 [**Failed**]

- **User Intent**: Count the number of IPv4 packets received on each ingress port and maintain separate counters per port using registers
- **Prompt Generator**:
  ```python
  detailed_prompt = (
        f"{high_level_prompt}. "
        "Generate complete, valid P4_16 code for BMv2 using the `v1model` architecture that compiles with `p4c-bm2-ss`. "
        "Define headers: `ethernet_t`, `ipv4_t`, and optionally `tcp_t` if needed. "
        "Use a `headers` struct to hold extracted headers and define an empty `metadata` struct. "
        "Use the built-in `VerifyChecksum<headers, metadata>()` — do not redefine it. "
        "If using registers, declare them globally (outside any control blocks) and access them using correct `bit<32>` indices. "
        "Cast `standard_metadata.ingress_port` to `bit<32>` if used as register index. "
        "To drop packets, use `standard_metadata.egress_spec = 0;`. "
        "Do not use `drop()` unless explicitly defined. "
        "End the program with:\n"
        "`V1Switch(MyParser(), VerifyChecksum<headers, metadata>(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;`"
    )
  ```
  
- **Common Errors**:  
- **Improvements**:

[Comparison of 1st and 5th Outputs](experiment4-failed/1_5_output.txt)

---

## Experiment 5 [**Success**]

- **Iteration No**: 3 (with compiler warning)
- **User Intent**: Count the number of IPv4 packets received on each ingress port and maintain separate counters per port using registers
- **Prompt Generator**:  
  ```python
  detailed_prompt = (
        f"{high_level_prompt}. "
        "Generate valid, complete P4_16 code that compiles with `p4c-bm2-ss` for the BMv2 `v1model` architecture. "
        "Use the following definitions:\n"
        "- Define `ethernet_t` and `ipv4_t` headers, and combine them in `struct headers`.\n"
        "- Define an empty `struct metadata {}`.\n"
        "- Define a parser named `MyParser` that extracts Ethernet and IPv4 headers using `etherType`.\n"
        "- Use control blocks named exactly: `MyVerifyChecksum`, `MyIngress`, `MyEgress`, `MyComputeChecksum`, `MyDeparser`.\n"
        "- Declare registers *outside* control blocks using `register<bit<32>>(256)` syntax.\n"
        "- Use register `read()` and `write()` correctly with `out` variable and matching index types (e.g., cast `ingress_port` to `bit<32>`).\n"
        "- Do **not** use `update_checksum()`. Leave `MyComputeChecksum` empty or correctly define `UpdateChecksum<>()` if needed.\n"
        "- Do **not** call `VerifyChecksum<>()` as a function — define `MyVerifyChecksum` control block instead.\n"
        "- Use `standard_metadata.egress_spec = 0;` for dropping packets.\n"
        "End exactly with:\n"
        "`V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;`"
    )
  ```
- **Common Errors**:

 
 [Comparison of 1st and 3rd Outputs](experiment5-success/1_3_output.txt)


---

## Experiment 6: Scope (Header Modification) Specific Prompt and Intents [**Success**]

- **Iteration No**: max: 9, min: 2  
- **User Intent**:  
  1) Rewrite destination IP to 10.0.0.2 if it is 10.0.0.1  
  2) Translate destination IP from 192.168.0.100 to 172.16.0.100 for NAT  
  3) Set source MAC to a fixed value and drop the packet if the destination IP is 8.8.8.8  

- **Prompt Generator**:
```python
def generate_nat_prompt(high_level_intent):
    prompt = (
        f"{high_level_intent.strip()}. "
        "Generate valid, complete P4_16 code targeting the BMv2 `v1model` architecture that compiles with `p4c-bm2-ss`. "
        "Include definitions for `ethernet_t` and `ipv4_t` headers and use a `headers` struct to hold them. "
        "Implement a parser named `MyParser` that extracts Ethernet and IPv4 headers. "
        "In the `MyIngress` block, modify headers based on match-action logic. "
        "Emit modified headers in the `MyDeparser`. "
        "Define an empty `metadata` struct. "
        "Use `V1Switch(...) main;` to wire together: `MyParser`, `MyVerifyChecksum`, `MyIngress`, `MyEgress`, `MyComputeChecksum`, `MyDeparser`."
    )
    return prompt
```

- **Output Comparisons**:
  - [Comparison of 1st and 9th Outputs](header_modification_NAT/experiment1-success/1_9_Output.txt)  
  - [Comparison of 1st and 3rd Outputs](header_modification_NAT/experiment2-success/1_3_output.txt)  
  - [Comparison of 1st and 2nd Outputs](header_modification_NAT/experiment1-success/1_2_output.txt)  

--- 
