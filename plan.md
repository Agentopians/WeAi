# Project Implementation Plan: Verifiable Agent Prompts with Agentic Operators

This document outlines a detailed, step-by-step guide to implement our PoC for verifiable agent prompts using EigenLayer AVS. The goal is to ensure that the AI-driven Ethereum newsletter generation agent (the “manager” agent) only executes when its governing prompt has been automatically verified by a network of agentic operators through an AVS. This plan is divided into several phases with clear tasks for each component.

---

## Phase 1: Solidity Contract Modifications

### 1.1 Rename Contracts
- **Action:** Rename the existing contracts to reflect the new use case.
  - Rename `contracts/src/IncredibleSquaringTaskManager.sol` to `contracts/src/NewsletterPromptTaskManager.sol`.
  - (Optionally, update service manager file similarly if applicable.)

### 1.2 Update Task Struct and Enum
- **Objective:** Recast the definition of a “task” so that it stores an agent prompt.
- **Changes:**
  - In the `Task` struct, remove (or comment out) the numeric field (e.g., `numberToBeSquared`), and add a new field:
    - `string agentPrompt;`
  - Modify the existing `enum` (or introduce one) to include a new type:
    - `enum TaskType { VerifyManagerInstructions, ... }`
  - Ensure the `createNewTask` function uses these new parameters:
    - Change its parameters to accept:
      - `TaskType _taskType,`
      - `string memory agentPrompt,`
      - and the other fields (quorumNumbers, quorumThresholdPercentage) remain.

### 1.3 Update Event Definitions (Optional)
- **Objective:** Enhance event clarity by including task type and prompt.
- **Changes:**
  - Update the event `NewTaskCreated` so that it now emits the Task struct that includes `taskType` and `agentPrompt`.
  - Optionally add events such as `PromptVerified` and `PromptRejected` for clarity.

---

## Phase 2: Aggregator Modifications (aggregator.py)

### 2.1 Add New Function for Prompt Verification Task
- **Objective:** Create a function to submit a “Verify Manager Instructions” task.
- **Action:** Implement `send_new_manager_instructions_verification_task(agent_prompt)` with:
  - `task_type` set to 0 (assuming `VerifyManagerInstructions` is index 0).
  - Pass the `agent_prompt` (string) instead of a number.
  - Use existing quorum settings (e.g., `nums_to_bytes([0])`, quorumThresholdPercentage as 100).

### 2.2 Adapt Signature Submission and Aggregation 
- **Objective:** Ensure that responses handling now interpret the verification status as boolean, rather than a computed number.
- **Action:** Check (and if needed adjust) the `submit_signature` function to accept the verification data structure (even if minimal changes are needed for the PoC).

### 2.3 Remove Unused Functions
- **Objective:** Disable functions used solely for the squaring example.
- **Action:** Comment out or remove `start_sending_new_tasks` and `send_new_task`.

---

## Phase 3: Operator Verification Agent Modifications (squaring_operator.py → prompt_operator.py)

### 3.1 Rename File and Class
- **Action:** Rename `squaring_operator.py` to `prompt_operator.py`.
- **Action:** Inside the file, change the class name from `SquaringOperator` to `PromptOperator`.

### 3.2 Update process_task_event Implementation
- **Objective:** Repurpose the operator’s logic from performing squaring to verifying an agent prompt.
- **Action:** Replace the content of the `process_task_event` function as follows:
  - Retrieve `task_id`, `task_type`, and `agent_prompt` from the event.
  - For `task_type == 0` (i.e. VerifyManagerInstructions):
    - Log the agent prompt to the console.
    - **Automated Policy Check Placeholder:**  
      For the PoC, you may start with a manual check (using `input()`), but the aim is to later replace this with policy-based automated checks.
      - Example: Use code to check if prompt length is acceptable and required keywords are present.
    - Set `verification_status` to `True` if approved or `False` if rejected.
    - Encode `[task_id, verification_status]` using `eth_abi.encode()`, compute the hash, sign it using the operator's BLS key.
    - Submit the signed verification verdict to the aggregator via a POST request.

---

## Phase 4: Autogen Workflow Integration (agents.py)

### 4.1 Define Manager Instructions
- **Action:** In `agents.py`, add a variable `manager_instructions` containing the detailed instructions for the `manager` agent. This text should describe how the agent should orchestrate tasks for newsletter generation.

### 4.2 Update create_society_of_mind_agent
- **Action:** Modify the function `create_society_of_mind_agent` to accept a parameter `manager_instructions` and pass that as the `system_message` when instantiating the `manager` agent.

### 4.3 Modify interact_freely_with_user to Integrate AVS Verification Flow
- **Action:** In `agents.py`, update the `interact_freely_with_user` function as follows:
  - Before initializing the SocietyOfMindAgent, instantiate the `Aggregator` and submit the manager instructions for AVS verification by calling `aggregator.send_new_manager_instructions_verification_task(manager_instructions)`.
  - Implement a simple polling mechanism (e.g., sleep and loop for up to 60 seconds) to wait for the verification outcome.
  - If the prompt is verified, proceed to initialize the SocietyOfMindAgent with the verified instructions; if not, abort the process or log an appropriate message.

---

## Phase 5: Testing and Verification

### 5.1 Deploy Updated Solidity Contracts
- **Action:** Compile your Solidity contracts using Foundry:
  - Run: `make build-contracts`
- **Action:** Deploy the contracts to your local Anvil chain using your deployment scripts.  
  **Important:** Update the contract addresses in your configuration files accordingly.

### 5.2 Run Aggregator, Operator, and Agents
- **Action:** Start `aggregator.py` in one terminal:
  - Command: `python aggregator.py`
- **Action:** Start `prompt_operator.py` in another terminal:
  - Command: `python prompt_operator.py`
- **Action:** Start `agents.py` in a third terminal with society mode:
  - Command: `python agents.py --mode society`
  
### 5.3 Monitor the Workflow
- **Expected Flow:**
  - `agents.py` submits the manager’s instructions for verification.
  - `prompt_operator.py` automatically (or via automated checks, if implemented) evaluates the prompt against the verification policies and sends back a signed verdict.
  - `aggregator.py` aggregates operator responses and the AVS contract records the outcome.
  - `agents.py` polls for the verification outcome; if verified, it proceeds to initialize the SocietyOfMindAgent and start the group chat.
- **Action:** Validate the process by checking terminal outputs and on-chain event logs to ensure that prompt verification is successful.

---

## Additional Considerations

- **Future Enhancements:**
  - Implement fully automated policy-based prompt verification in `prompt_operator.py` to replace manual input.
  - Expand the AVS to support additional task types (e.g., verifiable tool usage) once the PoC for prompt verification is stable.
  - Consider introducing operator model diversity for improved robustness once the core system is functional.

- **Time Constraints:**  
  Given our limited time, the focus for the initial PoC is on prompt verification. Later iterations can incorporate additional verification for tool usage and other aspects.

This document serves as the road map for our implementation. Each phase builds on the previous one, ensuring a phased, manageable development approach toward a fully verifiable, AI-driven newsletter system on EigenLayer.
