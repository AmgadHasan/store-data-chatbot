import os

import openai

from src.prompts import (
    ORDER_SYSTEM_MESSAGE,
)
from src.tools import (
    books_dataset_tools,
    llm_tools_map,
)
from src.utils import create_logger, handle_function_calls, log_execution_time

TEMPERATURE = 0
MAX_COMPLETION_TOKENS = 2048

logger = create_logger(logger_name="llm")

model = os.environ.get("CHAT_MODEL")
if not model:
    logger.error("CHAT_MODEL environment variable is not set.")
    raise ValueError("CHAT_MODEL environment variable is not set.")

client = openai.OpenAI()


@log_execution_time(logger=logger)
def create_completion(
    thread: list,
    system_message: str = ORDER_SYSTEM_MESSAGE,
    tools: list = books_dataset_tools,
):
    """
    Creates a completion response from the language model based on the system and user messages.

    Args:
        user_message (str): The conversation thread containing all messages.
        system_message (str): The system message to be included in the prompt.
        tools (list): A list of tools available for LLM to use.

    Returns:
        str: The response message generated by the LLM.

    Raises:
        Exception: If the LLM fails to generate a response.
    """
    try:
        logger.debug(f" create_completion |{system_message = }\n\n{thread = }")
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                *thread,
            ],
            model=model,
            n=1,
            temperature=TEMPERATURE,
            max_tokens=MAX_COMPLETION_TOKENS,
            tools=tools,
            tool_choice="auto"
        )

        logger.debug(f" create_completion | {completion = }")
        response = completion.choices[0].message
        return response
    except Exception as e:
        logger.error(
            f" create_completion | Error generating responses for chat thread '{thread}': {e}"
        )
        raise


@log_execution_time(logger=logger)
def process_user_question(user_question: str) -> str:
    """Handles user questions using an LLM"""
    thread = [{"role": "user", "content": user_question}]
    try:
        while True:
            logger.info(f"Processing user input: {thread}")
            response = create_completion(thread=thread, tools=books_dataset_tools)
            if not response.tool_calls:
                break
            thread.append(response)
            thread = handle_function_calls(
                function_map=llm_tools_map,
                response_message=response,
                thread=thread,
            )
        return response.content
    except Exception as e:
        logger.error(
            f"Error generating responses for user input:\n'{user_question}'\n\nError:\n{e}"
        )
        raise
