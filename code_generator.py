import os
import autogen
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug print
api_key = os.getenv("MISTRAL_API_KEY")
if api_key:
    print(f"API Key loaded (first 8 chars): {api_key[:8]}...")
else:
    print("No API key found!")

# Configure Mistral API
config_list = [
    {
        "model": os.getenv("MISTRAL_MODEL", "mistral-tiny"),
        "api_key": os.getenv("MISTRAL_API_KEY"),
        "base_url": "https://api.mistral.ai/v1",
        "api_type": "mistral"
    }
]

# Agent configurations
def create_agent_config(temperature: float = 0.7):
    return {
        "temperature": temperature,
        "config_list": config_list,
        "timeout": 300,
        "request_timeout": 300,
        "seed": 42
    }

# Create the agents with more focused system messages
developer = autogen.AssistantAgent(
    name="Developer",
    system_message="""Developer: Implement code following specifications and best practices.
    IMPORTANT: When implementing code, you must write it to files in the generated_code directory.""",
    llm_config=create_agent_config()
)

reviewer = autogen.AssistantAgent(
    name="Code_Reviewer",
    system_message="Review code quality and suggest critical improvements.",
    llm_config=create_agent_config()
)

# User proxy agent to manage the conversation
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    system_message="Coordinate the conversation efficiently.",
    human_input_mode="TERMINATE",
    code_execution_config={
        "work_dir": "generated_code",
        "use_docker": False
    },
    llm_config=create_agent_config()
)

def initiate_code_generation(requirements: str):
    """
    Start the code generation process with the given requirements.
    """
    try:
        # Create a chat group for the agents
        groupchat = autogen.GroupChat(
            agents=[user_proxy, developer, reviewer],
            messages=[],
            max_round=10,
            speaker_selection_method="round_robin"
        )
        
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=create_agent_config()
        )

        # Start the conversation with requirements
        user_proxy.initiate_chat(
            manager,
            message=f"""
            Generate code based on these requirements and save it to files in the generated_code directory:
            {requirements}
            
            Follow this process:
            1. Developer: Create the necessary files in the generated_code directory
            2. Reviewer: Review the implementation
            
            Focus on core functionality first.
            """
        )
    except Exception as e:
        print(f"Error during code generation: {str(e)}")
        if "maximum context length" in str(e):
            print("\nSuggestion: Try breaking down the requirements into smaller parts.")

if __name__ == "__main__":
    # Example usage with simpler requirements
    requirements = """
    Create a python program to execute hello world.
   
    """
    
    # Create the generated_code directory if it doesn't exist
    os.makedirs("generated_code", exist_ok=True)
    
    # Start the code generation process
    initiate_code_generation(requirements) 