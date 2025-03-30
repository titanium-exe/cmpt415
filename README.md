# cmpt415

## Experiment 1 
- No Success
- User Prompt : Parse Ethernet and IPv4 headers and forward packets unchanged (llm is given an easy task. complicated ones are still mystery...)
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


## Experiment 2 

















# Resources (still incomplete)

1) Prompt Style (in experiment 3): https://github.com/hzy46/NADA.git
