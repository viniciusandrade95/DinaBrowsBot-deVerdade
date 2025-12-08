import os
import requests

API_KEY = os.environ.get("MODEL_API_KEY")  # Your API key
BASE_URL = os.environ.get("MODEL_BASE_URL", "https://llm.lab.sspcloud.fr/api")
MODEL_ID = "gpt-oss:120b"  # Explicitly set the desired model


# --- Headers for the API request ---
def _build_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
    }


def start_chat():
    """Start a manual chat session with the configured OSS model."""
    if not API_KEY:
        raise RuntimeError("Set MODEL_API_KEY in your environment before running this test.")

    print("--- Starting Chat with GPT-OSS 120B ---")
    print(f"Model: {MODEL_ID}")
    print("Type 'quit' or 'exit' to end the conversation.\n")

    # Initialize conversation history with a system message
    conversation_history = [
        {"role": "system", "content": "You are a helpful and knowledgeable assistant."}
    ]

    while True:
        try:
            # 1. Get user input from the command line
            user_input = input("You: ")
            # 2. Check for exit command
            if user_input.lower() in ["quit", "exit"]:
                print("\nGoodbye! 👋")
                break
            # 3. Add the user's message to the history
            conversation_history.append({"role": "user", "content": user_input})
            # 4. Prepare the payload for the API
            chat_payload = {
                "model": MODEL_ID,
                "messages": conversation_history,
                "max_tokens": 1024,  # Increased for potentially longer chat responses
                "stream": False,
            }
            # 5. Send the request to the chat completions endpoint
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=_build_headers(),
                json=chat_payload,
                timeout=60,  # Increased timeout for a larger model
            )
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            # 6. Process the successful response
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            print(f"Assistant: {assistant_message}")
            # 7. Add the assistant's response to the history for context
            conversation_history.append({"role": "assistant", "content": assistant_message})
        except requests.exceptions.HTTPError as http_err:
            print(f"❌ HTTP Error: {http_err} - {response.text}")
        except requests.exceptions.RequestException as req_err:
            print(f"⚠️ Network Error: {req_err}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            break


# --- Main execution block ---
if __name__ == "__main__":
    start_chat()
