# Project Implementation Plan: Verifiable Agent Prompts with Agentic Operators
*(Revised Version - Smart Contracts Unchanged)*

This document provides a step-by-step plan to implement a Proof of Concept (PoC) for verifiable agent prompts using EigenLayer Autonomous Verifiable Services (AVS). The goal is to ensure that an AI-driven newsletter generation agent ("manager" agent) operates only after its instructions (prompt) have been verifiably reviewed and approved by a network of agentic operators.

**Important Note:** Due to recent issues and time constraints, we will *not* modify the existing Solidity smart contracts. Instead, we will repurpose the existing contract structure and fields to simulate prompt verification. This means we will focus our changes on the off-chain components: `aggregator.py`, `prompt_operator.py` (formerly `squaring_operator.py`), and `agents.py`.

---

## Phase 1: Smart Contract Context (No Code Changes)

Since we are *not* changing the smart contracts, understand the following:

- **Field Repurposing:**
    - The `numberToBeSquared` field in the `IncredibleSquaringTaskManager.sol` contract will now be used to represent a *fingerprint* of the agent prompt (e.g., a hash or numeric representation).
    - On-chain tasks and events will remain as they are defined in the original contracts. We will interpret their data differently in our off-chain code.

- **Rationale:** This approach minimizes risk and development time for this PoC while still demonstrating the core concept of verifiable agent prompts.

- **Future Consideration:** For a production system, modifying the smart contracts to explicitly support prompts and task types would be beneficial for clarity and correctness.

---

## Phase 2: Aggregator Modifications (`aggregator.py`)

### 2.1 Implement `send_new_manager_instructions_verification_task` Function

- **Objective:** Create a new function to submit a prompt verification task to the AVS using the existing `createNewTask` contract function.
- **Action:** Add a function `send_new_manager_instructions_verification_task(agent_prompt)` to `aggregator.py`.
    - Inside this function:
        - Define `task_type = 0` (representing "Verify Manager Instructions").
        - Convert the `agent_prompt` string into a numeric fingerprint. For example, you can:
            - Calculate the keccak256 hash of the `agent_prompt`.
            - Convert a portion of this hash into a `uint256` value.
        - Call the existing `createNewTask` function of the smart contract, passing:
            - The numeric fingerprint of the `agent_prompt` as the `numberToBeSquared` parameter.
            - Standard quorum parameters (e.g., `quorumThresholdPercentage = 100`, `quorumNumbers = nums_to_bytes([0])`).
    - **Note:** Document that this numeric value is *not* a number to be squared, but a representation of the agent prompt for verification.

### 2.2 Adapt Signature Handling

- **Objective:** Modify the aggregator to interpret operator responses as boolean verification verdicts (approve/reject) instead of squared numbers.
- **Action:** In functions like `submit_signature` and any response aggregation logic:
    - Update comments and variable names to reflect that the expected response is now a verification status (e.g., `verification_status` instead of `squared_number`).
    - Adjust any logging or processing steps to handle boolean verdicts.

### 2.3 Remove Unused Functions

- **Objective:** Remove or comment out functions related to the original squaring task, to simplify the code and avoid confusion.
- **Action:** Comment out or remove functions like `start_sending_new_tasks` and `send_new_task`.

---

## Phase 3: Operator Modifications (`prompt_operator.py` - renamed from `squaring_operator.py`)

### 3.1 Rename File and Class

- **Action:**
    - Rename the file `squaring_operator.py` to `prompt_operator.py`.
    - Rename the class `SquaringOperator` to `PromptOperator` within the file.

### 3.2 Implement Prompt Verification Logic in `process_task_event`

- **Objective:** Change the operator's behavior to verify agent prompts based on predefined policies instead of performing squaring calculations.
- **Action:** Modify the `process_task_event` function in `prompt_operator.py`:
    - Retrieve `task_id` and the `numberToBeSquared` value from the task event.
    - Reinterpret `numberToBeSquared` as the numeric fingerprint of the `agent_prompt`. You might need to reverse the fingerprinting process (if feasible) or simply acknowledge that the operator receives a fingerprint representing the prompt.
    - **Automated Policy Checks:** Implement automated checks to evaluate the `agent_prompt` (or its fingerprint) against predefined policies. Examples of policies for this PoC:
        - **Prompt Length:** Check if the prompt's length is within acceptable limits.
        - **Keyword Presence:** Verify if the prompt includes essential keywords (e.g., "Ethereum", "newsletter", "DeFi").
    - **Verification Verdict:** Based on the policy checks, determine a `verification_status`: `True` (approved) if policies are met, `False` (rejected) otherwise. For this PoC, you can start with simple rule-based policies.
    - **Sign and Submit Verdict:**
        - Encode `[task_id, verification_status]` using `eth_abi.encode()`.
        - Sign the encoded data using the operator's BLS key.
        - Submit the signed verdict to the aggregator via an HTTP POST request (using the existing mechanism).

---

## Phase 4: Autogen Workflow Integration (`agents.py`)

### 4.1 Define `manager_instructions`

- **Action:** In `agents.py`, define a string variable `manager_instructions`. This variable will hold the detailed instructions for the `manager` agent, outlining its role in newsletter generation.

### 4.2 Update `create_society_of_mind_agent`

- **Objective:** Modify the agent creation function to accept and use verified manager instructions.
- **Action:** Update `create_society_of_mind_agent(manager_instructions)` to:
    - Accept `manager_instructions` as a parameter.
    - Set the `system_message` of the `manager` agent to be the provided `manager_instructions`.

### 4.3 Integrate AVS Verification in `interact_freely_with_user`

- **Objective:** Implement the prompt verification workflow before starting agent interactions.
- **Action:** Modify `interact_freely_with_user` in `agents.py`:
    - Instantiate the `Aggregator`.
    - Call `aggregator.send_new_manager_instructions_verification_task(manager_instructions)` to submit the `manager_instructions` for verification.
    - Implement a polling mechanism (e.g., loop with `time.sleep()`) to wait for the verification outcome from the aggregator.
    - Check the verification outcome.
        - If verified (e.g., aggregator indicates success), proceed to create and initialize the `SocietyOfMindAgent` using the `manager_instructions`.
        - If not verified, log an error message and halt the agent initialization process.

---

## Phase 5: Configuration and Testing

### 5.1 Configuration Files

- **Aggregator Configuration (`config-files/aggregator.yaml`):**
    - Verify that contract addresses, quorum settings, and key file paths are correctly configured for your environment.
- **Operator Configuration (e.g., `config-files/operator.anvil.yaml`):**
    - Ensure blockchain endpoints and operator keys are correctly set.

- **Action:** Double-check all configuration files before running any components.

### 5.2 Run Components

- **Action:** Open separate terminals and start the following in order:
    1. Aggregator: `python aggregator.py`
    2. Prompt Operator: `python prompt_operator.py`
    3. Agents (Society Mode): `python agents.py --mode society`

### 5.3 Workflow Validation

- **Expected Flow:**
    1. `agents.py` submits `manager_instructions` for verification via the aggregator.
    2. Aggregator creates a task on-chain (using the repurposed `numberToBeSquared` field for the prompt fingerprint).
    3. `prompt_operator.py` receives the task, performs automated policy checks, and submits a signed verification verdict (approve/reject) to the aggregator.
    4. Aggregator aggregates verdicts.
    5. `agents.py` polls for the verification outcome. If verified, it initializes the `SocietyOfMindAgent` with the `manager_instructions` and starts the agent interaction.

- **Action:** Monitor terminal outputs and on-chain events to confirm the prompt verification process is working as expected.

---

## Additional Notes and Future Steps

- **PoC Focus:** This PoC prioritizes demonstrating verifiable prompt submission and automated operator verification.
- **Policy Refinement:** The automated policy checks in `prompt_operator.py` are basic for this PoC. Future iterations can incorporate more sophisticated AI-driven policy evaluations and operator model diversity.
- **Further Verifiability:** After prompt verification, consider extending verifiability to other aspects, such as agent tool usage and output content.
- **Smart Contract Evolution:** For a production-ready AVS, revisiting and modifying the smart contracts to natively support prompts and task types is recommended.

This revised `plan.md` provides a comprehensive guide for implementing the Verifiable Agent Prompts PoC, focusing on off-chain modifications and repurposing the existing smart contract infrastructure. Please review it with your team and let me know if you have any questions.
