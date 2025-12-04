from typing import List
import json
import re
from datetime import datetime

from .tools import Tool
from .model import create_model
from models.schemas import ThoughtStep, AgentResponse


class ReactAgent:
    def __init__(self, tools: List[Tool] = None, custom_system_prompt: str = None, max_iterations: int = 10):
        self.client = create_model()
        self.max_iterations = max_iterations
        
        self.tools = tools or []
        self.tool_registry = {tool.action_type: tool for tool in self.tools}
        
        tools_description = "\n\n".join(tool.get_tool_description() for tool in self.tools)
        tool_names = ", ".join(tool.action_type for tool in self.tools)
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        default_opening = "You are an AI assistant that follows the ReAct pattern."
        user_system_prompt = custom_system_prompt if custom_system_prompt else default_opening
        
        self.system_prompt = f"""{user_system_prompt}

You have access to these tools: {tool_names}

{tools_description}

IMPORTANT: Follow this EXACT format for every response.

When you need to use a tool:
Thought: [your reasoning]
Action: {{"action_type": "[tool_name]", "input": "[input_value]"}}

When you have the final answer (ONLY after gathering enough information):
Thought: I have enough information to answer.
Final Answer: [your complete answer]

Rules:
- Use ONE action at a time
- Wait for Observation before next step
- For simple queries, use retrieve_material first to get content, then give Final Answer
- Today's date is {current_date}
"""
    
    def execute_tool(self, action_type: str, action_input) -> str:
        tool = self.tool_registry.get(action_type)
        if not tool:
            return f"Error: Unknown tool '{action_type}'. Available: {list(self.tool_registry.keys())}"
        try:
            result = tool.run(action_input)
            # Truncate very long results
            if len(result) > 3000:
                result = result[:3000] + "\n...[truncated]"
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run(self, query: str, debug: bool = False) -> AgentResponse:
        thought_process: List[ThoughtStep] = []
        history = ""
        
        for iteration in range(self.max_iterations):
            if debug:
                print(f"\n=== Iteration {iteration + 1} ===")
            
            prompt = f"Question: {query}\n\n{history}Continue:\n"
            
            response_text = self.client.chat_completion(self.system_prompt, prompt)
            
            if debug:
                print(f"LLM Response:\n{response_text[:500]}")
            
            # Check for Final Answer
            if "Final Answer:" in response_text:
                final_match = re.search(r"Final Answer:\s*(.*)", response_text, re.DOTALL)
                if final_match:
                    final_answer = final_match.group(1).strip()
                    return AgentResponse(thought_process=thought_process, final_answer=final_answer)
            
            # Parse Thought and Action
            thought_match = re.search(r"Thought:\s*(.*?)(?=Action:|Final Answer:|$)", response_text, re.DOTALL)
            action_match = re.search(r"Action:\s*(\{.*?\})", response_text, re.DOTALL)
            
            thought = thought_match.group(1).strip() if thought_match else ""
            
            if action_match:
                try:
                    action_data = json.loads(action_match.group(1))
                    action_type = action_data.get("action_type", "")
                    action_input = action_data.get("input", "")
                    
                    if debug:
                        print(f"Action: {action_type}, Input: {action_input}")
                    
                    observation = self.execute_tool(action_type, action_input)
                    
                    if debug:
                        print(f"Observation: {observation[:200]}...")
                    
                    # Add to history
                    history += f"Thought: {thought}\n"
                    history += f"Action: {json.dumps(action_data)}\n"
                    history += f"Observation: {observation}\n\n"
                    
                    thought_process.append(ThoughtStep(
                        thought=thought,
                        action_type=action_type,
                        observation=observation[:500]
                    ))
                    
                except json.JSONDecodeError as e:
                    if debug:
                        print(f"JSON Error: {e}")
                    history += f"Thought: {thought}\nObservation: Error parsing action JSON. Use exact format.\n\n"
            else:
                # No action found, add thought to history
                history += f"Thought: {thought}\nObservation: No valid action. Use Action or Final Answer.\n\n"
        
        # If we get here, return what we have
        return AgentResponse(
            thought_process=thought_process,
            final_answer="I couldn't complete the task. Please try a more specific question."
        )
