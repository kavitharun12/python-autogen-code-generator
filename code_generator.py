import os
import autogen
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

# Configure OpenAI API
config_list = [
    {
        "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
]

# Agent configurations
def create_agent_config(temperature: float = 0.7):
    return {
        "seed": 42,  # for reproducibility
        "temperature": temperature,
        "config_list": config_list,
        "timeout": 600,
    }

# Create the agents
product_manager = autogen.AssistantAgent(
    name="Product_Manager",
    system_message="""You are a Product Manager who:
    1. Understands user requirements thoroughly
    2. Creates detailed specifications
    3. Ensures all requirements are clear and well-defined
    4. Communicates with the architect to ensure feasibility""",
    llm_config=create_agent_config(),
)

architect = autogen.AssistantAgent(
    name="Architect",
    system_message="""You are a Software Architect who:
    1. Designs system architecture based on requirements
    2. Creates implementation plans
    3. Makes technology choices
    4. Ensures scalability and maintainability
    5. Provides clear technical specifications to the developer""",
    llm_config=create_agent_config(),
)

developer = autogen.AssistantAgent(
    name="Developer",
    system_message="""You are a Developer who:
    1. Implements code based on technical specifications
    2. Follows best practices and coding standards
    3. Writes clean, efficient, and well-documented code
    4. Handles error cases and edge conditions""",
    llm_config=create_agent_config(),
)

reviewer = autogen.AssistantAgent(
    name="Code_Reviewer",
    system_message="""You are a Code Reviewer who:
    1. Reviews code for quality and best practices
    2. Identifies potential issues and bugs
    3. Suggests improvements
    4. Ensures code meets requirements""",
    llm_config=create_agent_config(),
)

qa_engineer = autogen.AssistantAgent(
    name="QA_Engineer",
    system_message="""You are a QA Engineer who:
    1. Creates and executes test cases
    2. Verifies functionality against requirements
    3. Identifies edge cases and potential issues
    4. Provides feedback on code quality""",
    llm_config=create_agent_config(),
)

# User proxy agent to manage the conversation
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    system_message="A user proxy that helps coordinate the conversation between agents and manages code generation tasks.",
    human_input_mode="TERMINATE",
    code_execution_config={
        "work_dir": "generated_code",
        "use_docker": False,
    },
)

def initiate_code_generation(requirements: str):
    """
    Start the code generation process with the given requirements.
    """
    # Create a chat group for the agents
    groupchat = autogen.GroupChat(
        agents=[user_proxy, product_manager, architect, developer, reviewer, qa_engineer],
        messages=[],
        max_round=50,
    )
    
    manager = autogen.GroupChatManager(groupchat=groupchat)

    # Start the conversation with requirements
    user_proxy.initiate_chat(
        manager,
        message=f"""
        Please help generate code based on the following requirements:
        {requirements}
        
        Follow this process:
        1. Product Manager: Analyze requirements and create detailed specifications
        2. Architect: Design system architecture and create implementation plan
        3. Developer: Implement the code according to specifications
        4. Code Reviewer: Review the implementation
        5. QA Engineer: Verify the implementation meets requirements
        
        Generate all necessary files and ensure the code is complete and working.
        """,
    )

if __name__ == "__main__":
    # Example usage
    requirements = """
    Create a simple web API that:
    1. Provides CRUD operations for a todo list
    2. Stores data in a JSON file
    3. Includes basic error handling
    4. Has input validation
    """
    
    # Create the generated_code directory if it doesn't exist
    os.makedirs("generated_code", exist_ok=True)
    
    # Start the code generation process
    initiate_code_generation(requirements) 