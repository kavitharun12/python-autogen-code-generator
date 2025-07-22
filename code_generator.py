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
    import re
    import shutil
    try:
        # Clean up the generated_code directory before generating new files
        gen_dir = "generated_code"
        if os.path.exists(gen_dir):
            for filename in os.listdir(gen_dir):
                file_path = os.path.join(gen_dir, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

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
        chat_result = user_proxy.initiate_chat(
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

        # Parse the Developer's output for code blocks and filenames
        if hasattr(chat_result, 'chat_history'):
            messages = chat_result.chat_history
        elif isinstance(chat_result, list):
            messages = chat_result
        else:
            messages = []

        code_blocks = []
        for msg in messages:
            if hasattr(msg, 'content'):
                content = msg.content
            elif isinstance(msg, dict) and 'content' in msg:
                content = msg['content']
            else:
                continue
            # Look for code blocks with or without filenames
            for match in re.finditer(r'```(?:python)?\s*([\w_.\\/-]+)?\n([\s\S]*?)```', content):
                filename = match.group(1)
                code = match.group(2)
                code_blocks.append((filename.strip() if filename else None, code.strip()))

        # Write code blocks to files
        wrote_any = False
        unnamed_count = 0
        valid_extensions = {'.java', '.py', '.js', '.ts', '.kt', '.go', '.c', '.cpp', '.cs', '.rb', '.php', '.html', '.css', '.json', '.xml', '.yml', '.yaml', '.sh', '.bat', '.ps1'}
        language_names = {'java', 'python', 'javascript', 'typescript', 'kotlin', 'go', 'c', 'cpp', 'csharp', 'ruby', 'php', 'html', 'css', 'json', 'xml', 'yaml', 'shell', 'bash', 'powershell'}
        for idx, (filename, code) in enumerate(code_blocks):
            use_default = False
            class_name = None
            subfolder = None
            ext = None
            if filename:
                # Remove any leading 'generated_code/' or 'generated_code\\' from filename
                cleaned_filename = re.sub(r'^generated_code[\\/]+', '', filename)
                ext = os.path.splitext(cleaned_filename)[1].lower()
                # If filename is just a language name or has no valid extension, use default
                if cleaned_filename.lower() in language_names or not ext or ext not in valid_extensions:
                    use_default = True
                else:
                    file_path = os.path.join("generated_code", cleaned_filename)
            else:
                use_default = True

            if use_default:
                # Try to extract class name from code for Java, Python, etc.
                java_class_match = re.search(r'(?:public\s+)?class\s+(\w+)', code)
                python_class_match = re.search(r'class\s+(\w+)', code)
                # Try to extract package for Java
                java_package_match = re.search(r'package\s+([\w\.]+);', code)
                # Try to extract module for Python
                python_module_match = re.search(r'^#\s*module:\s*([\w_]+)', code, re.MULTILINE)
                if java_class_match:
                    class_name = java_class_match.group(1)
                    ext = '.java'
                    # If package found, use as subfolder
                    if java_package_match:
                        subfolder = java_package_match.group(1).replace('.', os.sep)
                elif python_class_match:
                    class_name = python_class_match.group(1)
                    ext = '.py'
                    if python_module_match:
                        subfolder = python_module_match.group(1)
                else:
                    # Try to infer purpose from comments or first function/def
                    # Look for a comment at the top
                    comment_match = re.search(r'^(//|#)\s*(.+)', code)
                    if comment_match:
                        purpose = comment_match.group(2).strip().replace(' ', '_').replace('.', '').replace('/', '').replace('\\', '')
                        class_name = purpose[:30] if purpose else f"main{unnamed_count if unnamed_count else ''}"
                    else:
                        # Try to use first function/def name
                        func_match = re.search(r'def\s+(\w+)', code)
                        if func_match:
                            class_name = func_match.group(1)
                        else:
                            class_name = f"main{unnamed_count if unnamed_count else ''}"
                    # Guess extension from code
                    if 'public static void main' in code or 'System.out.println' in code:
                        ext = '.java'
                    elif 'def ' in code:
                        ext = '.py'
                    elif '<html' in code.lower():
                        ext = '.html'
                    else:
                        ext = '.txt'
                # Compose file path
                if subfolder:
                    file_path = os.path.join("generated_code", subfolder, f"{class_name}{ext}")
                else:
                    file_path = os.path.join("generated_code", f"{class_name}{ext}")
                unnamed_count += 1

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            print(f"[Output] Wrote file: {file_path}")
            wrote_any = True

        if not wrote_any:
            print("[Warning] No code blocks found in the Developer's output.")
    except Exception as e:
        print(f"Error during code generation: {str(e)}")
        if "maximum context length" in str(e):
            print("\nSuggestion: Try breaking down the requirements into smaller parts.")

if __name__ == "__main__":
    # Read requirements from a document in the inputRequirement folder
    input_folder = "inputRequirement"
    # Find the first text or markdown file in the folder
    requirements_file = None
    if os.path.exists(input_folder):
        for fname in os.listdir(input_folder):
            if fname.lower().endswith(('.txt', '.md')):
                requirements_file = os.path.join(input_folder, fname)
                break
    if not requirements_file:
        raise FileNotFoundError("No requirements document (.txt or .md) found in inputRequirement folder.")

    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = f.read()

    # Create the generated_code directory if it doesn't exist
    os.makedirs("generated_code", exist_ok=True)

    # Start the code generation process
    initiate_code_generation(requirements)