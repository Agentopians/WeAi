import os
import time
import json
import logging
from random import randbytes
import requests
import yaml
from web3 import Web3
import eth_abi
from eth_account import Account
from eigensdk.chainio.clients.builder import BuildAllConfig, build_all
from eigensdk.crypto.bls.attestation import KeyPair
from eigensdk._types import Operator
from routellm import inference # This import is not used and can be removed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptOperator: # Class name is now PromptOperator
    def __init__(self, config):
        self.config = config
        self.__load_bls_key()
        self.__load_ecdsa_key()
        self.__load_clients()
        self.__load_task_manager()
        if config["register_operator_on_startup"] == 'true':
            self.register()
        # operator id can only be loaded after registration
        self.__load_operator_id()

    def register(self):
        operator = Operator(
            address=self.config["operator_address"],
            earnings_receiver_address=self.config["operator_address"],
            delegation_approver_address="0x0000000000000000000000000000000000000000",
            staker_opt_out_window_blocks=0,
            metadata_url="",
        )
        self.clients.el_writer.register_as_operator(operator)
        self.clients.avs_registry_writer.register_operator_in_quorum_with_avs_registry_coordinator(
            operator_ecdsa_private_key=self.operator_ecdsa_private_key,
            operator_to_avs_registration_sig_salt=randbytes(32),
            operator_to_avs_registration_sig_expiry=int(time.time()) + 3600,
            bls_key_pair=self.bls_key_pair,
            quorum_numbers=[0],
            socket="Not Needed",
        )

    def start(self):
        logger.info("Starting Operator...")
        event_filter = self.task_manager.events.NewTaskCreated.create_filter(
            fromBlock="latest"
        )
        while True:
            logger.info("Polling for new task events...") # ADDED LOGGING
            new_events = event_filter.get_new_entries()
            logger.info(f"Number of new events received: {len(new_events)}") # ADDED LOGGING
            for event in new_events:
                logger.info(f"New task created: {event}")
                self.process_task_event(event)
            time.sleep(3)

    def process_task_event(self, event):
        logger.info("Entering process_task_event function") # ADDED LOGGING - CHECK IF THIS APPEARS
        task_id = event["args"]["taskIndex"]
        task_type = event["args"]["task"]["taskType"] # Get task_type from event
        agent_prompt = event["args"]["task"]["agentPrompt"] # Get agent prompt from event

        if task_type == 0:  # Assuming VerifyManagerInstructions is enum index 0
            logger.info(f"New Manager Instructions Verification Task created: Task Index {task_id}")
            logger.info(f"Agent Prompt to Review:\\n{agent_prompt}")

            # --- Automated Policy Checks ---
            is_valid_length = len(agent_prompt) <= 200 # Example: Max length 200 characters
            required_keywords = ["ethereum", "defi", "l2"]
            has_required_keywords = any(keyword in agent_prompt.lower() for keyword in required_keywords)

            policy_length_satisfied = is_valid_length
            policy_keyword_satisfied = has_required_keywords

            verification_status = policy_length_satisfied and policy_keyword_satisfied # Approve only if ALL policies pass

            logger.info(f"Policy Check Results:")
            logger.info(f"  Length Policy Satisfied: {policy_length_satisfied}")
            logger.info(f"  Keyword Policy Satisfied: {policy_keyword_satisfied}")
            logger.info(f"  Overall Verification Status: {'Approved' if verification_status else 'Rejected'}")

            encoded = eth_abi.encode(["uint32", "bool"], [task_id, verification_status]) # Encode task_id and verification_status
            hash_bytes = Web3.keccak(encoded)
            signature = self.bls_key_pair.sign_message(msg_bytes=hash_bytes).to_json()
            logger.info(f"Operator Verdict: {'Approved' if verification_status else 'Rejected'}, Task ID: {task_id}, Signature: {signature}")

            data = { # Data to send to aggregator
                "task_id": task_id,
                "verification_status": verification_status, # Send boolean verification status
                "signature": signature,
                "block_number": event['blockNumber'],
                "operator_id": "0x" + self.operator_id.hex(),
            }
            logger.info(f"Submitting Operator Verdict for Task {task_id} to aggregator: {data}")
            # prevent submitting task before initialize_new_task gets completed on aggregator
            time.sleep(3)\n            url = f'http://{self.config["aggregator_server_ip_port_address"]}/signature'
            requests.post(url, json=data)
        else: # Handle other task types if you add more later - for now, just log unknown task type
            logger.warning(f"Unknown Task Type ({task_type}) received for Task Index {task_id}. Ignoring.")


    def __load_bls_key(self):
        bls_key_password = os.environ.get("OPERATOR_BLS_KEY_PASSWORD", "")
        if not bls_key_password:
            logger.warning("OPERATOR_BLS_KEY_PASSWORD not set. using empty string.")

        self.bls_key_pair = KeyPair.read_from_file(
            self.config["bls_private_key_store_path"], bls_key_password
        )

    def __load_ecdsa_key(self):
        ecdsa_key_password = os.environ.get("OPERATOR_ECDSA_KEY_PASSWORD", "")
        if not ecdsa_key_password:
            logger.warning("OPERATOR_ECDSA_KEY_PASSWORD not set. using empty string.")

        with open(self.config["ecdsa_private_key_store_path"], "r") as f:
            keystore = json.load(f)
        self.operator_ecdsa_private_key = Account.decrypt(keystore, ecdsa_key_password).hex()

    def __load_clients(self):
        cfg = BuildAllConfig(
            eth_http_url=self.config["eth_rpc_url"],
            avs_name="incredible-squaring",
            registry_coordinator_addr=self.config["avs_registry_coordinator_address"],
            operator_state_retriever_addr=self.config["operator_state_retriever_address"],
            prom_metrics_ip_port_address=self.config["eigen_metrics_ip_port_address"],
        )
        self.clients = build_all(cfg, self.operator_ecdsa_private_key, logger)

    def __load_task_manager(self):
        web3 = Web3(Web3.HTTPProvider(self.config["eth_rpc_url"]))

        service_manager_address = self.clients.avs_registry_writer.service_manager_addr
        with open("abis/IncredibleSquaringServiceManager.json") as f:
            service_manager_abi = f.read()
        service_manager = web3.eth.contract(
            address=service_manager_address, abi=service_manager_abi
        )

        task_manager_address = (
            service_manager.functions.incredibleSquaringTaskManager().call()
        )
        with open("abis/IncredibleSquaringTaskManager.json") as f:
            task_manager_abi = f.read()
        self.task_manager = web3.eth.contract(address=task_manager_address, abi=task_manager_abi)

    def __load_operator_id(self):
        self.operator_id = self.clients.avs_registry_reader.get_operator_id(
            self.config["operator_address"]
        )

if __name__ == "__main__":
    with open("config-files/operator.anvil.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.BaseLoader)

    PromptOperator(config=config).start() # Class name is now PromptOperator
