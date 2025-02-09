# Agent Architecture: Verifiable Agent Prompts

This document illustrates the architecture of the Week in Ethereum News AI Edition system, now focusing on the **Verifiable Agent Prompts** implementation using EigenLayer AVS and Agentic Operators.

```mermaid
graph LR
    A[Newsletter Creator] --> B{Define Agent Prompt & Policies}
    B --> C[Submit Prompt & Policies to AVS]
    C --> D{NewsletterPromptTaskManager Contract}
    D --> E{Verification Task Created}
    E --> F[Agentic Operators]
    F --> G{Verification Agents (in Operators)}
    G --> H{Automated Policy Check}
    H --> I{Generate Verdict (Pass/Fail)}
    I --> J[Submit Verdict & Signature to Aggregator]
    F --> J
    J --> K{Aggregator}
    K --> L{Aggregate Verdicts}
    K --> D
    L --> M{AVS Contract Records Outcome}
    D --> M
    M --> N{Check Verification Outcome in agents.py}
    N -- Verified --> O[Autogen Newsletter Agent]
    N -- Rejected --> P[Halt Newsletter Generation & Notify Creator]

    style D fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#f0f,stroke:#333,stroke-width:2px
    style K fill:#ccf,stroke:#333,stroke-width:2px
    style N fill:#ccf,stroke:#ccf,stroke-width:2px
```

## Component Descriptions

### Verifiable Agent Prompt Workflow Components

- **Newsletter Creator:** The entity or individual responsible for defining the Agent Prompt and Verification Policies for each newsletter issue. This is the starting point of the verifiable workflow.
- **Agent Prompt & Policies:**  The set of instructions (prompt) that guides the Autogen Newsletter Agent, along with the predefined Verification Policies that the prompt must adhere to.
- **AVS (NewsletterPromptTaskManager Contract):** The Solidity smart contract deployed as an EigenLayer Autonomous Verifiable Service (AVS). In this architecture, it is specifically the `NewsletterPromptTaskManager` contract. It is responsible for:
    - Receiving and storing Agent Prompts and Verification Policies.
    - Creating Verification Tasks.
    - Recording verification outcomes provided by the Aggregator.
    - Enforcing access control and pausing/unpausing functionalities.
- **Verification Task Created:** Represents the on-chain event indicating that a new prompt verification task has been created in the AVS contract, triggered by the Newsletter Creator submitting a prompt.
- **Agentic Operators:**  Represent a decentralized network of entities participating in the EigenLayer AVS. In our Proof of Concept, these are simulated by running `prompt_operator.py`.  Each Operator is responsible for deploying and running a Verification Agent.
- **Verification Agents (in Operators):** Specialized AI agents deployed and run by Agentic Operators. These agents are responsible for:
    - Receiving Prompt Verification Tasks.
    - Automatically checking if the submitted Agent Prompt adheres to the predefined Verification Policies.
    - Generating a Verdict (\"Pass\" or \"Fail\") based on the policy checks.
    - Cryptographically signing the Verdict using the Operator's BLS key.
- **Automated Policy Check:**  The process performed by Verification Agents to automatically evaluate the Agent Prompt against the defined Verification Policies. This involves techniques like keyword analysis, length checks, and potentially more advanced NLP-based policy evaluations.
- **Generate Verdict (Pass/Fail):** The outcome of the Automated Policy Check, indicating whether the Agent Prompt is deemed valid (\"Pass\") or invalid (\"Fail\") according to the Verification Policies.
- **Submit Verdict & Signature to Aggregator:** Each Verification Agent submits its generated Verdict (Pass/Fail) and its cryptographic signature to the Aggregator component.
- **Aggregator:** The off-chain component (`aggregator.py`) responsible for:
    - Receiving signed Verdicts from Agentic Operators.
    - Aggregating the Verdicts and signatures.
    - Determining the overall Verification Outcome based on the aggregated verdicts (e.g., majority vote).
    - Submitting the aggregated Verification Outcome to the AVS contract.
- **Aggregate Verdicts:** The process within the Aggregator of combining individual operator verdicts to determine a final, collective verification outcome.
- **AVS Contract Records Outcome:** The AVS contract (`NewsletterPromptTaskManager`) stores the final Verification Outcome (Verified/Rejected) on-chain, providing a permanent and auditable record.
- **Check Verification Outcome in `agents.py`:** The `agents.py` script (our main Autogen workflow) queries the AVS contract to check the recorded Verification Outcome for the submitted Agent Prompt.
- **Autogen Newsletter Agent:** The main AI agent (Society of Mind agent in `agents.py`) responsible for generating the Ethereum newsletter content.  It is **conditionally executed** only if the Agent Prompt has been verifiably approved by the AVS.
- **Halt Newsletter Generation & Notify Creator:** If the Verification Outcome is \"Rejected\", the newsletter generation process is halted, and the Newsletter Creator is notified, preventing the generation of content based on an unverified or rejected prompt.

## Data Flow

This section outlines the flow of information and control within the Verifiable Agent Prompt architecture:

1.  **Prompt and Policy Definition:** The Newsletter Creator defines the Agent Prompt and associated Verification Policies.
2.  **Prompt Submission to AVS:** The Newsletter Creator submits the Agent Prompt and Policies to the `NewsletterPromptTaskManager` contract.
3.  **Verification Task Creation:** The AVS contract emits an event indicating a new Verification Task has been created.
4.  **Task Distribution to Agentic Operators:** Agentic Operators, monitoring the AVS contract for new tasks, receive the Verification Task details (Agent Prompt and Policies).
5.  **Automated Policy Check by Verification Agents:** Each Agentic Operator's Verification Agent automatically analyzes the Agent Prompt against the Verification Policies.
6.  **Verdict Generation and Signing:** Each Verification Agent generates a Verdict (Pass/Fail) and cryptographically signs it.
7.  **Verdict Submission to Aggregator:** Verification Agents submit their signed Verdicts to the Aggregator.
8.  **Verdict Aggregation and Outcome Determination:** The Aggregator aggregates the Verdicts and determines the overall Verification Outcome (Verified/Rejected).
9.  **Outcome Recording on AVS Contract:** The Aggregator submits the aggregated Verification Outcome to the `NewsletterPromptTaskManager` contract, which records it on-chain.
10. **Outcome Check in `agents.py`:** The `agents.py` script queries the AVS contract to retrieve the Verification Outcome.
11. **Conditional Agent Execution:**
    - If the Outcome is **Verified**: The `agents.py` script proceeds to execute the Autogen Newsletter Agent, using the verifiably approved Agent Prompt to guide content generation.
    - If the Outcome is **Rejected**: The `agents.py` script halts the newsletter generation process and notifies the Newsletter Creator.
12. **Newsletter Generation and Distribution (if Verified):** If the prompt is verified, the Autogen Newsletter Agent generates the newsletter content, which is then distributed through the intended channels (e.g., Telegram, email).

## Agent Roles (in the Autogen Workflow - Newsletter Generation)

- **Manager Agent:**  The primary AI agent orchestrating the newsletter creation process.  Its behavior is now guided by **Verifiably Approved Agent Prompts**, ensuring its instructions have been reviewed and validated by the Agentic Operator network.
- **Critic Agent:** Reviews plans and results generated by the Manager Agent, ensuring quality, completeness, and alignment with the newsletter's objectives.
- **Web Scraper Agent:** Gathers relevant information from the web based on instructions from the Manager Agent, focusing on reliable sources and structured data extraction.
- **Coder Agent:** (Currently placeholder/under development) Intended for future use in data analysis, code execution, and potentially code-assisted content generation.
- **Telegram Poster Agent:** Automates the distribution of the generated newsletter content to a Telegram channel.
- **Twitter Poster Agent:** (Currently commented out/future feature) Intended for automated posting to Twitter (X) in future iterations.

## Operator Roles (in the AVS - Prompt Verification)

- **Agentic Operators:** Entities participating in the EigenLayer AVS, responsible for providing the verifiable prompt review service. In our Proof of Concept, these are simulated by running `prompt_operator.py`.
- **Verification Agents (within Operators):** Specialized AI agents deployed by Agentic Operators. These agents automatically perform the **Automated Policy Check**, evaluating Agent Prompts against predefined **Verification Policies** and generating **Verdicts**.

This architecture provides a robust framework for building a trustworthy and transparent AI-driven newsletter, leveraging EigenLayer AVS to ensure verifiable control over the AI content generation process through Verifiable Agent Prompts and Agentic Operators.
