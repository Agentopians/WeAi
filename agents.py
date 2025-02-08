#!/usr/bin/env python3

import os
import json
from dotenv import load_dotenv
import autogen
from autogen import ConversableAgent, UserProxyAgent
from autogen.agentchat.contrib.capabilities.teachability import Teachability
from autogen.formatting_utils import colored
from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.retrieve_utils import TEXT_FORMATS
import requests
import pandas as pd
from typing import Dict, Any
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from autogen import ConversableAgent, UserProxyAgent, register_function
import asyncio
import nest_asyncio
from mytools import (
    TwitterPostAgent,
    TelegramPostAgent,
    WebScraperAgent
)
from aggregator import Aggregator # ADDED IMPORT
import time # ADDED IMPORT

nest_asyncio.apply()
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

config_list = [
    {
        'model': 'gpt-4o-mini',
        'api_key': openai_api_key,
        'max_tokens': 4096,
        'temperature': 0.7
    }
]

llm_config = {
    "config_list": config_list,
    "cache_seed": None,
    "timeout": 600
}

manager_instructions = """You are the task orchestrator. For each task:
    1. Create initial plan of what analysis is needed
    2. Ask coder to do some analysis if needed
    3. Wait for critic to review your plan
    4. Based on critic's feedback:
        If it is needed:
        - Ask web_scraper for relevant information
    5. Show results to critic
    6. Based on critic's feedback, might need to:
        If it is needed:
        - Get more info from web_scraper
    7. When critic approves final results:
        - Ask telegram-poster to post a brief tweet summarizing the findings
    8. Only finish when tweet is posted""" # ADDED manager_instructions - Step 4.2

def create_group_chat(manager_instructions): # MODIFIED - Accept manager_instructions - Step 4.3
    """Creates a group chat with proper task management flow"""
    def safe_termination_check(x):
        if not x or not isinstance(x, dict):
            return False
        content = x.get("content")
        if not content or not isinstance(content, str):
            return False
        return content.find("TERMINATE") >= 0

    manager = autogen.AssistantAgent(
        name="manager",
        system_message=manager_instructions, # MODIFIED - Use manager_instructions - Step 4.3
        llm_config=llm_config,
        is_termination_msg=safe_termination_check,
    )

    critic = autogen.AssistantAgent(
        name="critic",
        system_message="""You review plans and results:
        1. When reviewing plans:
            - Check if all necessary data is being collected
            - Suggest additional data sources
            - Point out potential analysis gaps
        2. When reviewing results:
            - Ask coder to do some analysis if needed
            - Verify data quality from samples
            - Check if analysis answers the original question
            - Suggest improvements or additional analysis
        3. Be specific about what needs to be improved
        4. Make sure the coder always run the code and give the results to manager""",
        llm_config=llm_config,
        is_termination_msg=safe_termination_check,
    )

    web_scraper = WebScraperAgent(
        name="web-scraper",
        system_message="""You gather relevant information:
        1. Focus on what manager requests
        2. Use reliable sources
        3. Return structured results""",
        is_termination_msg=safe_termination_check,
    )

    coder = autogen.UserProxyAgent(
        name="coder",
        human_input_mode="NEVER",
        system_message="""You write and execute Python code:
        1. Always make sure you manage to run the code
        2. Show your work and results""",
        code_execution_config={"work_dir": "coding", "use_docker": False}, # REWRITTEN LINE - Step 4.4
        default_auto_reply="",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    )

    #twitter_agent = TwitterPostAgent(
    #    name="twitter-poster",
    #    system_message="""You post Twitter updates:
    #    1. Maintain brand voice
    #    2. Follow engagement best practices
    #    3. Return posting results""",
    #    is_termination_msg=safe_termination_check,
    #    llm_config=llm_config  # Now only passed once
    #)

    telegram_agent = TelegramPostAgent(
        name="telegram-poster",
        system_message="""You post Telegram updates:
        1. Maintain brand voice
        2. Follow engagement best practices
        3. Return posting results
        4. Posts content should be related to topic not the internal conversation""",
        is_termination_msg=safe_termination_check,
        llm_config=llm_config  # Optional, if applicable
    )

    groupchat = autogen.GroupChat(
        agents=[manager, critic, web_scraper, coder, telegram_agent],
        messages=[],
        speaker_selection_method="round_robin",
        allow_repeat_speaker=False,
        max_round=15,
    )

    group_manager = autogen.GroupChatManager(
        groupchat=groupchat,
        is_termination_msg=safe_termination_check,
        llm_config=llm_config,
    )

    return group_manager

def create_society_of_mind_agent(manager_instructions): # MODIFIED - Accept manager_instructions - Step 4.3
    """Creates Society of Mind with manager orchestrating everything"""
    group_manager = create_group_chat(manager_instructions) # MODIFIED - Pass manager_instructions

    society_of_mind_agent = SocietyOfMindAgent(
        name="society_of_mind",
        chat_manager=group_manager,
        llm_config=llm_config,
    )

    nested_chat_queue = [
        {
            "recipient": group_manager,
            "summary_method": "reflection_with_llm",
        }
    ]

    trigger_user = UserProxyAgent(
        name="user_proxy",
        human_input_mode="ALWAYS",
        code_execution_config=False,
        is_termination_msg=lambda x: True,
    )

    society_of_mind_agent.register_nested_chats(
        nested_chat_queue,
        trigger=trigger_user
    )

    return society_of_mind_agent

def interact_freely_with_user(mode="society"): # MODIFIED - Step 4.4
    """Starts a chat between the user and selected agent type."""
    print(colored("\\nInitializing agent system...", "light_cyan"))

    if mode == "society":
        aggregator_config = { # Load your aggregator config - ADJUST PATHS IF NEEDED
            "eth_rpc_url": "http://localhost:8545", # Or your Anvil RPC URL
            "aggregator_server_ip_port_address": "localhost:8090", # Or your aggregator server address
            "ecdsa_private_key_store_path": "tests/keys/aggregator.ecdsa.key.json", # Adjust path
            "avs_registry_coordinator_address": "0xa82fF9aFd8f496c3d6ac40E2a0F282E47488CFc9", # Adjust address
            "operator_state_retriever_address": "0x95401dc811bb5740090279Ba06cfA8fcF6113778" # Adjust address
        }
        aggregator = Aggregator(aggregator_config) # Initialize Aggregator (ensure you've imported Aggregator class)

        task_index = aggregator.send_new_manager_instructions_verification_task(manager_instructions) # Submit prompt for verification
        print(colored(f"\\nSubmitted Manager Instructions for AVS Verification. Task Index: {task_index}. Waiting for operator verdicts...", "light_cyan"))

        # Polling for Verification Status (Simple PoC Polling - Replace with event listener for production)
        verification_status = None
        start_time = time.time()
        while time.time() - start_time < 60: # Poll for up to 60 seconds (adjust timeout as needed)
            # In a real app, you'd query the contract for verification status based on task_index
            # For this PoC, we'll just wait and assume operators will respond in time.
            time.sleep(5) # Check every 5 seconds
            # In a more advanced PoC, you would query the contract's events or state
            # to determine the verification outcome and aggregated signature