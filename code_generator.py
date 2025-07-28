import os
import autogen
from dotenv import load_dotenv
import re
import shutil

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
        "config_list": [
            {
                "model": os.getenv("MISTRAL_MODEL", "mistral-medium"),  # Use a more capable model if available
                "api_key": os.getenv("MISTRAL_API_KEY"),
                "base_url": "https://api.mistral.ai/v1",
                "api_type": "mistral"
            }
        ],
        "timeout": 300,
        "request_timeout": 300,
        "seed": 42
    }

# Add Architect agent for project structure and architecture planning
architect = autogen.AssistantAgent(
    name="Architect",
    system_message="""
    Architect: Analyze the input requirements and design the overall project structure and architecture. 
    Output a clear directory and file structure, and specify the main components and their responsibilities. 
    Ensure the structure follows best practices for a Spring Boot project in Java 21, using Maven conventions. 
    Pass your plan to the Developer agent for implementation.
    """,
    llm_config=create_agent_config()
)

developer = autogen.AssistantAgent(
    name="Developer",
    system_message="""
    Developer: Implement the code following the architecture and structure provided by the Architect. 
    Write all code to files in the generated_code directory, following the specified structure. 
    Use Spring Boot (Java 21) and Cucumber for BDD. 
    Pass your implementation to the Reviewer agent for review.
    """,
    llm_config=create_agent_config()
)

reviewer = autogen.AssistantAgent(
    name="Code_Reviewer",
    system_message="""
    Reviewer: Review the implementation for code quality, correctness, and adherence to best practices. 
    Suggest and make critical improvements. 
    Pass the reviewed code to the QA agent for test generation.
    """,
    llm_config=create_agent_config()
)

qa_agent = autogen.AssistantAgent(
    name="QA_Agent",
    system_message="""
    QA Agent: Generate automated test cases for the generated code. 
    Ensure tests cover core functionality and edge cases. 
    Save all test files in the appropriate test directory under generated_code. 
    Use Cucumber and JUnit for testing.
    """,
    llm_config=create_agent_config()
)

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
        gen_dir = "generated_code"
        # Clean up the generated_code directory (remove everything)
        if os.path.exists(gen_dir):
            for filename in os.listdir(gen_dir):
                file_path = os.path.join(gen_dir, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
        os.makedirs(gen_dir, exist_ok=True)

        # Create a chat group for the agents (Architect -> Developer -> Reviewer -> QA)
        groupchat = autogen.GroupChat(
            agents=[user_proxy, architect, developer, reviewer, qa_agent],
            messages=[],
            max_round=16,
            speaker_selection_method="round_robin"
        )

        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=create_agent_config()
        )

        # Start the conversation with requirements, instructing the pipeline
        chat_result = user_proxy.initiate_chat(
            manager,
            message=f"""
            The following is the input requirement for a Java Spring Boot project:
            {requirements}

            Pipeline:
            1. Architect: Analyze the requirements and design the project structure and architecture. Output a clear directory and file structure, and specify the main components and their responsibilities.
            2. Developer: Implement the code following the architecture and structure provided by the Architect. Use Spring Boot (Java 21) and Cucumber for BDD.
            3. Reviewer: Review the implementation for code quality, correctness, and adherence to best practices. Suggest and make critical improvements.
            4. QA Agent: Generate automated test cases for the generated code. Ensure tests cover core functionality and edge cases. Use Cucumber and JUnit for testing.

            Focus on production-quality code and best practices at each step.
            """
        )

        # ... existing code for parsing and writing code blocks ...
    except Exception as e:
        print(f"Error during code generation: {str(e)}")
        if "maximum context length" in str(e):
            print("\nSuggestion: Try breaking down the requirements into smaller parts.")
