# Project Implementation Plan: Verifiable Agent Prompts with Agentic Operators
*(Original Version - Smart Contract Modifications Included)*

This document outlines a detailed, step-by-step guide to implement our Proof of Concept (PoC) for verifiable agent prompts using EigenLayer AVS. The goal is to ensure that the AI-driven newsletter generation agent (the “manager” agent) only executes when its governing prompt has been verifiably reviewed and approved by a network of agentic operators. This plan includes modifications to the Solidity smart contracts to explicitly support agent prompt verification.

---

## Phase 1: Solidity Contract Modifications

### 1.1 Rename Contracts
- **Action:** Rename the existing contracts to reflect the new use case.
  - Rename `contracts/src/IncredibleSquaringTaskManager.sol` to `contracts/src/NewsletterPromptTaskManager.sol`.
  - Rename `contracts/src/IIncredibleSquaringTaskManager.sol` to `contracts/src/INewsletterPromptTaskManager.sol`.
  - (Optionally, update service manager file similarly if applicable.)

### 1.2 Update Task Struct and Enum
- **Objective:** Recast the definition of a “task” so that it stores an agent prompt and task type.
- **Files to Modify:** `contracts/src/INewsletterPromptTaskManager.sol`, `contracts/src/NewsletterPromptTaskManager.sol`
- **Changes:**

    **In `contracts/src/INewsletterPromptTaskManager.sol` (Interface):**
    - Add a new `enum` at the top of the interface:
      ```solidity
      enum TaskType {
          VerifyManagerInstructions
      }
      ```
    - Modify the `Task` struct to include `taskType` and `agentPrompt`:
      ```solidity
      struct Task {
          TaskType taskType;
          string agentPrompt;
          uint32 taskCreatedBlock;
          bytes quorumNumbers;
          uint32 quorumThresholdPercentage;
      }
      ```
    - Update the `createNewTask` function signature to accept `TaskType` and `agentPrompt`:
      ```solidity
      function createNewTask(
          TaskType _taskType,
          string calldata agentPrompt,
          uint32 quorumThresholdPercentage,
          bytes calldata quorumNumbers
      ) external;
      ```

    **In `contracts/src/NewsletterPromptTaskManager.sol` (Main Contract):**
    - In the `createNewTask` function, update the function signature to match the interface and correctly assign values to the new `taskType` and `agentPrompt` fields in the `Task` struct:
      ```solidity
      function createNewTask(
          TaskType _taskType,
          string memory agentPrompt,
          uint32 quorumThresholdPercentage,
          bytes calldata quorumNumbers
      ) external onlyTaskGenerator {
          // create a new task struct
          Task memory newTask;
          newTask.taskType = _taskType;
          newTask.agentPrompt = agentPrompt;
          newTask.taskCreatedBlock = uint32(block.number);
          newTask.quorumThresholdPercentage = quorumThresholdPercentage;
          newTask.quorumNumbers = quorumNumbers;
      }
      ```

### 1.3 Update Event Definitions (Optional)
- **Objective:** Enhance event clarity by including task type and prompt in events.
- **Files to Modify:** `contracts/src/INewsletterPromptTaskManager.sol`, `contracts/src/NewsletterPromptTaskManager.sol`
- **Changes:**
  - Update the `NewTaskCreated` event in both interface and main contract to emit the `Task` struct which now includes `taskType` and `agentPrompt`.
  - Optionally, add new events such as `PromptVerified` and `PromptRejected` for more explicit logging of verification outcomes.

---

## Phase 2: Aggregator Modifications (`aggregator.py`)

### 2.1 Update Function for Prompt Verification Task
- **Objective:** Modify the aggregator to submit a “Verify Manager Instructions” task with the new contract interface.
- **File to Modify:** `aggregator.py`
- **Action:** Update `send_new_manager_instructions_verification_task(agent_prompt)` in `aggregator.py`:
  - Set `task_type` to `0` (assuming `VerifyManagerInstructions` is the first enum value).
  - Pass the `agent_prompt` string directly to the `createNewTask` function, along with other required parameters (`quorumThresholdPercentage`, `quorumNumbers`).

### 2.2 Adapt Signature Submission and Aggregation
- **Objective:** Ensure that response handling now correctly interprets the verification status as a boolean, rather than a computed number.
- **File to Modify:** `aggregator.py`
- **Action:** Review and adjust the `submit_signature` function and response aggregation logic in `aggregator.py` to:
  - Handle the verification status as a boolean value.
  - Update logging and variable names to reflect the new verification process.

### 2.3 Remove Unused Functions
- **Objective:** Disable functions used solely for the squaring example.
- **File to Modify:** `aggregator.py`
- **Action:** Comment out or remove `start_sending_new_tasks` and `send_new_task` in `aggregator.py`.

---

## Phase 3: Operator Verification Agent Modifications (`prompt_operator.py` - renamed from `squaring_operator.py`)

### 3.1 Rename File and Class
- **Action:**
    - Rename `squaring_operator.py` to `prompt_operator.py`.
    - Inside, change the class name from `SquaringOperator` to `PromptOperator`.

### 3.2 Update `process_task_event` Implementation
- **Objective:** Repurpose the operator’s logic from squaring to verifying agent prompts based on policies.
- **File to Modify:** `prompt_operator.py`
- **Action:** Modify the `process_task_event` function in `prompt_operator.py`:
  - Retrieve `task_id`, `task_type`, and `agent_prompt` directly from the event data (as the contract now explicitly includes these).
  - Check if `task_type` is `VerifyManagerInstructions`.
  - Implement **Automated Policy Checks** to evaluate the `agent_prompt`. Examples:
    - **Length check:** Ensure the prompt’s character count is below a threshold.
    - **Keyword check:** Ensure the prompt contains required keywords (e.g., "Ethereum", "DeFi").
  - Determine `verification_status` (`True` for approved, `False` for rejected) based on policy checks.
  - Encode `[task_id, verification_status]` using `eth_abi.encode()`, sign it, and submit to the aggregator.

---

## Phase 4: Autogen Workflow Integration (`agents.py`)

### 4.1 Define Manager Instructions
- **Action:** In `agents.py`, define `manager_instructions` as a string containing the detailed instructions for the `manager` agent.

### 4.2 Update `create_society_of_mind_agent`
- **Objective:** Ensure the verified instructions are used when creating the `manager` agent.
- **File to Modify:** `agents.py`
- **Action:** Modify `create_society_of_mind_agent` to accept `manager_instructions` and set it as the `system_message` for the `manager` agent.

### 4.3 Integrate AVS Prompt Verification Flow in `interact_freely_with_user`
- **Objective:** Implement the prompt verification workflow before agent interaction starts.
- **File to Modify:** `agents.py`
- **Action:** Update `interact_freely_with_user` in `agents.py`:
  - Instantiate the `Aggregator`.
  - Call `aggregator.send_new_manager_instructions_verification_task(manager_instructions)` to submit the prompt for verification.
  - Implement polling to wait for the verification outcome.
  - If verified, initialize `SocietyOfMindAgent` with `manager_instructions`; if not, log an error and halt.

---

## Phase 5: Testing and Verification

### 5.1 Deploy Updated Solidity Contracts
- **Action:** Compile and deploy the modified Solidity contracts to your local Anvil chain using Foundry.
  - Run: `make build-contracts`
  - Update contract addresses in configuration files (`config-files/aggregator.yaml`, `config-files/operator.anvil.yaml`).

### 5.2 Run Aggregator, Operator, and Agents
- **Action:** Start the off-chain components in separate terminals:
  - Aggregator: `python aggregator.py`
  - Prompt Operator: `python prompt_operator.py`
  - Agents (Society Mode): `python agents.py --mode society`

### 5.3 Monitor the Workflow
- **Expected Flow:**
  - `agents.py` submits `manager_instructions` for verification.
  - Aggregator creates a `VerifyManagerInstructions` task on-chain, including the prompt.
  - `prompt_operator.py` receives the task, performs policy checks, and submits a signed verdict.
  - Aggregator aggregates responses and records the outcome.
  - `agents.py` polls for verification outcome; if verified, it initializes `SocietyOfMindAgent` and starts interaction.
- **Action:** Validate the process by checking terminal outputs and on-chain events.

---

## Phase 6: Configuration

- **Configuration Files:**
  - **Aggregator:** Ensure `config-files/aggregator.yaml` has correct contract addresses, quorum settings, and key paths.
  - **Operator:** Ensure `config-files/operator.anvil.yaml` has correct blockchain endpoints and operator keys.
- **Action:** Double-check all config files before running.

---

## Additional Notes and Future Steps

- **PoC Focus:** This PoC focuses on verifiable prompt submission and automated operator verification.
- **Policy Refinement:** Policy checks in `prompt_operator.py` are basic for this PoC. Future iterations can include more advanced AI-driven policies and operator model diversity.
- **Further Verifiability:** Extend verifiability to agent tool usage and output content in future phases.
- **Smart Contract Evolution:**  The modified smart contracts in this plan are a step towards a production-ready AVS. Further refinement and security audits would be necessary.

This updated `plan.md` now reflects our intention to modify the smart contracts and provides a complete guide for implementing the Verifiable Agent Prompts PoC. Please review it with your team, and let me know if you have any questions or require further adjustments.

path/to/plan.md
