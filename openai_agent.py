import os

from autogen import ConversableAgent

agent = ConversableAgent(
    "chatbot",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    code_execution_config=False,
    function_map=None, 
    human_input_mode="NEVER", 
)


def inference(prompt):
    return agent.generate_reply(messages=[{"content": prompt, "role": "user"}])