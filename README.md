# cmpt415

## Experiment 1  (The starter)
- No Success
- User Prompt : Parse Ethernet and IPv4 headers and forward packets unchanged (llm is given an easy task. complicated ones are still a mystery...)
- Prompt generator :  
                       
                        detailed_prompt = (
                                    f"{high_level_prompt}. {more_details}. "
                                    "Write valid, complete P4_16 code for the BMv2 `v1model` architecture that compiles with `p4c-bm2-ss`. "
                                    "Include all required blocks: headers, metadata, parser, ingress, egress, deparser, VerifyChecksum, ComputeChecksum. "
                                    "Define an empty `struct metadata {}`. "
                                    "End with `V1Switch(...) main;` using all six components exactly:\n"
                                    "`V1Switch(MyParser(), VerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;`"
                                )

- No of Iterations: 5 

- Observation: In the 5th iteration 1 of the 4 (maybe more) errors were solved.
- A little Success despite having explicit prompt in the begining, llm gave me improved code after 5th iteration after taking feedback from p4c. The feedback was  same error 5 times. so stubborn!

- Improvement : 
                V1Switch(
                    MyParser(),
                    MyVerifyChecksum(),
                    MyIngress(),
                    MyEgress(),
                    MyComputeChecksum(),
                    MyDeparser()
                ) main;

- 1st and 5th output comparision :  experiment1/1-and-5-summary.txt


## Experiment 2 (The Repeater)
- No Success
- User Prompt : Count all IPv4 packets received and store the count in a register 
- Prompt generator :  
                  
                  
                    detailed_prompt = (
                                f"{high_level_prompt}. "
                                "Generate valid, complete P4_16 code targeting the BMv2 v1model architecture that compiles with p4c-bm2-ss. "
                                "Include precisely:\n"
                                "- Header definitions (e.g., ethernet_t).\n"
                                "- Empty metadata struct.\n"
                                "- Parser block named MyParser.\n"
                                "- Empty control blocks named exactly: MyVerifyChecksum, MyIngress, MyEgress, MyComputeChecksum.\n"
                                "- Deparser named MyDeparser.\n"
                                "End exactly with:\n"
                                "V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;"
                    )

- I noticed that llm always makes standard 3 errors over and over again for any prompt in all the scripts.
- Even after explicitly setting the requirement in the prompt: 
    - Always incomplete: 
            V1Switch(
                MyParser(),
                MyIngress(),
                MyEgress(),
                MyDeparser()
            ) main;
    - Control Signature Mismatches: Incorrect parameter names/types in control blocks (e.g., Headers instead of headers, missing metadata).
    - Naming Inconsistencies: Non-standard or mis-capitalized identifiers (e.g., Meta vs. metadata, MyChecksum vs. MyComputeChecksum).


- 1st and 5th output comparision :  experiment1/1-and-5-summary.txt


## Experiment 3 (The Winner)

- Finally Success, because I followed NADA framework style prompting. 



## Resources (still incomplete)

1) Prompt Style (in experiment 3): https://github.com/hzy46/NADA.git  (and no wonder why i got the right code in 3 iterations)




**Course**: CMPT 415 
**Date**: March 30, 2025  
**Author**: Ekamleen

---

## Experiment 1 (The Starter)

- **Success**: None  
- **User Prompt**: "Parse Ethernet and IPv4 headers and forward packets unchanged." (The LLM was given a simple task; more complex ones remain unexplored.)  
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

- **Number of Iterations**: 5  
- **Observation**: In the fifth iteration, one of at least four errors was resolved. Despite an explicit prompt provided initially, the LLM only improved the code after the fifth iteration, incorporating feedback from `p4c-bm2-ss`. The feedback consisted of the same error repeated five times, indicating persistent issues.  
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

- **Comparison of 1st and 5th Outputs**: Refer to `experiment1/1-and-5-summary.txt`.  

---

## Experiment 2 (The Repeater)

- **Success**: None  
- **User Prompt**: "Count all IPv4 packets received and store the count in a register."  
- **Prompt Generator**:  

    ```python
    detailed_prompt = (
        f"{high_level_prompt}. "
        "Generate valid, complete P4_16 code targeting the BMv2 v1model architecture that compiles with p4c-bm2-ss. "
        "Include precisely:\n"
        "- Header definitions (e.g., ethernet_t).\n"
        "- Empty metadata struct.\n"
        "- Parser block named MyParser.\n"
        "- Empty control blocks named exactly: MyVerifyChecksum, MyIngress, MyEgress, MyComputeChecksum.\n"
        "- Deparser named MyDeparser.\n"
        "End exactly with:\n"
        "V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;"
    )
    ```

- **Observation**: The LLM consistently produced three recurring errors across all prompts and scripts, even with explicit requirements specified:  
  - **Incomplete Pipeline**:  

      ```p4
      V1Switch(
          MyParser(),
          MyIngress(),
          MyEgress(),
          MyDeparser()
      ) main;
      ```

  - **Control Signature Mismatches**: Incorrect parameter names or types in control blocks (e.g., `Headers` instead of `headers`, missing `metadata`).  
  - **Naming Inconsistencies**: Non-standard or mis-capitalized identifiers (e.g., `Meta` instead of `metadata`, `MyChecksum` instead of `MyComputeChecksum`).  
- **Comparison of 1st and 5th Outputs**: Refer to `experiment1/1-and-5-summary.txt`.  

---

## Experiment 3 (The Winner)

- **Success**: Achieved, due to adopting the NADA framework-style prompting.  

---

## Resources (Incomplete)

1. **Prompt Style (Experiment 3)**: [NADA Framework](https://github.com/hzy46/NADA.git)  
  


