import os
import litellm
from typing import Dict, Any, Optional

#####################
# PROMPT TEMPLATES ##
#####################

TWEET_EDIT_PROMPT = """You are an expert at crafting engaging tweet replies. You need to edit a reply tweet based on specific instructions.

ORIGINAL TWEET:
{original_tweet}

CURRENT REPLY:
{generated_reply}

{context_section}
EDIT INSTRUCTIONS:
{edit_instructions}

Please provide ONLY the edited reply with no additional text, explanations, or formatting. The output should be ready to post directly as a tweet reply."""


#####################
# HELPER FUNCTIONS ##
#####################


def _format_prompt(template: str, **kwargs) -> str:
    """Helper function to format prompts with given parameters."""
    # Special handling for context which is optional
    if "context" in kwargs and kwargs["context"]:
        context_text = f"""CONTEXT:
{kwargs['context']}

"""
        kwargs["context_section"] = context_text
    else:
        kwargs["context_section"] = ""

    return template.format(**kwargs)


######################
# LLM API FUNCTIONS ##
######################


def call_llm(
    prompt: str,
    model: str = "claude-3-7-sonnet-20250219",
    temperature: float = 0.7,
) -> str:
    """Generic function to call LLM API with given prompt."""
    try:
        # Configure LiteLLM
        litellm.set_verbose = False

        # Make the API call
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=1000,
        )

        # Extract the response text
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error calling LLM: {e}")
        return f"Error: Failed to call LLM. {str(e)}"


#####################
# PUBLIC FUNCTIONS ##
#####################


def edit_tweet_reply(
    original_tweet: str,
    generated_reply: str,
    edit_instructions: str,
    context: Optional[str] = None,
) -> str:
    """
    Uses LLM to edit a generated tweet reply based on user instructions.
    """
    # Format the prompt
    prompt = _format_prompt(
        TWEET_EDIT_PROMPT,
        original_tweet=original_tweet,
        generated_reply=generated_reply,
        edit_instructions=edit_instructions,
        context=context,
    )

    # Call the LLM
    return call_llm(prompt)
