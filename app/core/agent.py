import ollama
import json
import re
import os
from app.utils.erp_tools import TOOL_REGISTRY

MODEL = os.getenv("OLLAMA_MODEL", "llama3")

SYSTEM_PROMPT = """
You are an ERPNext Assistant with read-only access.
You have access to these tools:
1. erp_get(doctype, name) - Get details of a specific document.
2. erp_list(doctype) - List documents.
3. erp_count(doctype) - Count documents.

RULES FOR erp_list:
- If the user query implies a search (e.g., "name starts with"), use filters.
- If the user query requests specific fields (e.g., "status"), use fields
- For fields, send a list of field names (e.g., fields=["name", "status"]).
- For filters, send a list of conditions (e.g., filters=[["status", "=", "Open"]]).
- Whenever a user asks for customers, always add "customer_name" field to show names.
- Send either fields or filters, but never both.
If you need data to answer, output a TOOL CALL in this EXACT format:
[[TOOL: tool_name(arg1, arg2)]]

Example: [[TOOL: erp_get("Customer", "CUST-001")]]
NEVER add anything like [[TOOL: erp_list(doctype="Customer")]]. Always use something like [[TOOL: erp_list("Customer")]]
If you have the data or don't need tools, just answer normally.
"""

def parse_tool_call(text):
    pattern = r"\[\[TOOL:\s*(\w+)\((.*?)\)\]\]"
    match = re.search(pattern, text)
    if match:
        tool_name = match.group(1)
        args_str = match.group(2)
        args = [arg.strip().strip('"').strip("'") for arg in args_str.split(',')]
        args = [a for a in args if a]
        return tool_name, args
    return None, None

def run_agent(user_query: str):
    # --- DEBUG: Start of Turn ---
    print("\n" + "="*50)
    print(f"🔹 [DEBUG] RECEIVED QUERY: {user_query}")
    print("="*50)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    # First turn: Ask Ollama
    response = ollama.chat(model=MODEL, messages=messages)
    ai_content = response['message']['content']
    
    # --- DEBUG: AI's Raw Thought ---
    print(f"\n🧠 [DEBUG] RAW AI RESPONSE:\n{ai_content}\n")

    tool_name, args = parse_tool_call(ai_content)

    if tool_name:
        # --- DEBUG: Tool Decision ---
        print(f"🛠️  [DEBUG] TOOL DETECTED: {tool_name}")
        print(f"📥 [DEBUG] ARGUMENTS PASSED: {args}")

        if tool_name in TOOL_REGISTRY:
            try:
                tool_func = TOOL_REGISTRY[tool_name]
                # The actual tool execution happens here
                tool_result = tool_func(*args)
                
                # Convert result to string
                tool_output_str = json.dumps(tool_result)
                
                # --- DEBUG: Tool Result ---
                # We truncate the output if it's too long so it doesn't flood your terminal
                display_output = (tool_output_str[:200] + '...') if len(tool_output_str) > 200 else tool_output_str
                print(f"✅ [DEBUG] TOOL RESULT SENT TO AI: {display_output}")

            except Exception as e:
                tool_output_str = f"Error executing tool: {str(e)}"
                print(f"❌ [DEBUG] TOOL ERROR: {tool_output_str}")

            # Second turn: Feed result back to Ollama
            follow_up_prompt = (
                f"The tool {tool_name} returned this JSON data: {tool_output_str}. "
                "Using this data, answer the user's original question."
            )
            
            messages.append({"role": "assistant", "content": ai_content})
            messages.append({"role": "user", "content": follow_up_prompt})

            final_response = ollama.chat(model=MODEL, messages=messages)
            
            print(f"\n🤖 [DEBUG] FINAL ANSWER GENERATED")
            print("="*50 + "\n")
            
            return final_response['message']['content']
        else:
            print(f"⚠️ [DEBUG] UNKNOWN TOOL REQUESTED: {tool_name}")
            return f"Error: AI tried to use unknown tool '{tool_name}'"
    else:
        print(f"\n🤖 [DEBUG] NO TOOL NEEDED, FINAL ANSWER:\n")
    print("="*50 + "\n")
    return ai_content