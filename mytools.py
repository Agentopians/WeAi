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
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from autogen import ConversableAgent
import pypdf
import rapidocr_onnxruntime
import os
import tweepy
from autogen import ConversableAgent, register_function

import asyncio
from typing import Optional, Dict, Any, Callable
from twikit import Client
import os
import requests
from autogen import ConversableAgent, register_function

nest_asyncio.apply()

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
x_api_key = os.getenv("X-API-KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

TWITTER_API_KEY=os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET_KEY=os.getenv("TWITTER_API_SECRET_KEY")
TWITTER_ACCESS_TOKEN=os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN=os.getenv("TWITTER_BEARER_TOKEN")
TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_THREAD_ID=os.getenv("TELEGRAM_THREAD_ID")

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

def save_config():
    """Save configuration to JSON file"""
    os.makedirs('config', exist_ok=True)
    with open('config/config_list.json', 'w') as f:
        json.dump(config_list, f, indent=4)

class TelegramPostAgent(ConversableAgent):
    def __init__(self, name="telegram_post_agent", system_message=None, llm_config=None, **kwargs):
        default_system_message = """I am a Telegram posting specialist that shares updates in a group.
        When posting:
        1. Maintain brand voice
        2. Follow engagement best practices
        3. Return posting results"""
        
        super().__init__(name=name, system_message=system_message or default_system_message, llm_config=llm_config, **kwargs)

        # Register the post_message function
        register_function(
            self.post_message,
            caller=self,
            executor=self,
            name="post_message",
            description="Posts content to a Telegram group and returns the result"
        )

    def post_message(self, content: str, reply_to_message_id: int = None) -> dict:
        """Posts a message to the Telegram group (optionally replies to another message)."""
        result = {"success": False, "content": None, "error": None}

        try:
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            thread_id = os.getenv('TELEGRAM_THREAD_ID')

            # Check if required environment variables are set
            if not bot_token or not chat_id:
                raise ValueError("Environment variables for Telegram bot token and chat ID are required.")

            # API URL for sending messages
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # Prepare the payload
            payload = {
                "chat_id": chat_id,
                "message_thread_id": thread_id,
                "text": content,
                "parse_mode": "Markdown"  # Allows for Markdown formatting in the message
            }

            if reply_to_message_id is not None:
                payload["reply_to_message_id"] = reply_to_message_id  # Only include if replying to a message

            # Send request to Telegram API
            response = requests.post(url, json=payload)
            data = response.json()

            # Check if the response from the API is successful
            if response.status_code == 200 and data.get("ok"):
                result["success"] = True
                result["content"] = content
            else:
                result["error"] = data.get("description", "Unknown error")

        except Exception as e:
            result["error"] = str(e)

        return result

class TwitterPostAgent(ConversableAgent):
    def __init__(self, name="twitter_post_agent", system_message=None, **kwargs):
        default_system_message = """I am a Twitter posting specialist that shares updates and news.
        When posting:
        1. Maintain brand voice
        2. Follow engagement best practices
        3. Return posting results"""
        
        super().__init__(
            name=name,
            system_message=system_message or default_system_message,
            **kwargs
        )
        
        # Initialize Twitter client
        try:
            self.twitter_client = tweepy.Client(
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET_KEY'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
                wait_on_rate_limit=True  # Helps with rate limits
            )
            self.twitter_client.get_me()  # Test auth
        except Exception as e:
            print(f"Twitter auth failed: {e}")
            self.twitter_client = None
            
        # Register the post_tweet function
        register_function(
            self.post_tweet,
            caller=self,
            executor=self,
            name="post_tweet",
            description="Posts content to Twitter and returns the result"
        )
    
    def post_tweet(self, content: str) -> dict:
        """Posts a tweet and returns the result with proper error handling"""
        result = {
            "success": False,
            "content": None,
            "error": None
        }
        
        try:
            if not self.twitter_client:
                raise ValueError("Twitter client not initialized")
                
            # Clean and truncate content
            text = content.strip()
            if len(text) > 280:
                text = text[:277] + "..."
                
            # Post tweet
            response = self.twitter_client.create_tweet(text=text)
            
            if hasattr(response, 'data'):
                result["success"] = True
                result["content"] = text
            else:
                result["error"] = "No response data from Twitter"
                
        except Exception as e:
            result["error"] = str(e)
            
        return result

class WebScraperAgent(ConversableAgent):
    def __init__(self, name="web_scraper_agent", system_message=None, **kwargs):
        default_system_message = """I am a web scraping specialist that extracts market data and analysis.
        When scraping fails:
        1. Try alternative sources
        2. Return any partial successes
        3. Report what was found and what failed"""
        super().__init__(
            name=name,
            system_message=system_message or default_system_message,
            llm_config=llm_config,
            **kwargs
        )
        
        register_function(
            self.web_scraper,
            caller=self,
            executor=self,
            name="web_scraper",
            description="A tool that scrapes web content using AI to extract specific information based on prompts"
        )
    
    def web_scraper(self, prompt: str, url: str) -> dict:
        """Scrapes web content with improved error handling"""
        results = {
            "success": False,
            "partial_success": False,
            "data": [],
            "errors": [],
            "url": url
        }
        
        try:
            scraper = SmartScraperGraph(
                prompt=prompt,
                source=url,
                config={"llm": {"api_key": openai_api_key, "model": "openai/gpt-4o-mini"}}
            )
            result = scraper.run()
            
            if result:
                results["success"] = True
                results["data"].append(result)
            else:
                results["errors"].append("No data returned from scraper")
                
        except Exception as e:
            print(f"Scraping error for {url}: {str(e)}")
            results["errors"].append(str(e))
            
        results["partial_success"] = bool(results["data"])
        return results