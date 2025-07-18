# Autonomous Code Generator

This project uses the AutoGen framework to create an autonomous code generation system that can understand requirements and generate code through multi-agent collaboration.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the code generator:
```bash
python code_generator.py
```

The system uses multiple agents to:
1. Understand requirements
2. Plan implementation
3. Generate code
4. Review and test code
5. Make improvements based on feedback

## Architecture

The system consists of multiple agents:
- Product Manager: Understands requirements and creates specifications
- Architect: Designs system architecture and implementation plan
- Developer: Generates actual code
- Reviewer: Reviews code and provides feedback
- QA: Tests the generated code

Each agent has specific responsibilities and collaborates with others to produce high-quality code. 