**Course**: CMPT 415  
**Date**: March 30, 2025  
**Author**: Ekamleen  

---

## Experiment 1 [**Failed**]

- **User Intent**:  
- **Prompt Generator**:  
    ```python
    detailed_prompt = (
        f"{high_level_prompt}. {more_details}. "
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

- **Comparison of 1st and 5th Outputs**:  
  Refer to `experiment1/1-and-5-summary.txt`.

---

## Experiment 2 [**Success**]

- **Iteration No**:  
- **User Intent**:  
- **Prompt Generator**:  
  // code from the file  
- **Common Errors**:

---

## Experiment 3 [**Success**]

- **Iteration No**:  
- **User Intent**:  
- **Prompt Generator**:  
  // code from the file  
- **Common Errors**:

---

## Experiment 4 [**Failed**]

- **User Intent**:  
- **Prompt Generator**:  
  // code from the file  
- **Common Errors**:  
- **Improvements**:

---

## Experiment 5 [**Success**]

- **Iteration No**:  
- **User Intent**:  
- **Prompt Generator**:  
  // code from the file  
- **Common Errors**:

