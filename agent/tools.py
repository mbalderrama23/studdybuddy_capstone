"""
Base Tool class for AgentPro framework.
All StudyBuddy tools inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """
    Abstract base class for all AgentPro tools.
    Each tool must define:
    - action_type: unique identifier for this tool
    - get_tool_description(): description for LLM to understand when/how to use it
    - run(input): execute the tool with given input
    """
    
    @property
    @abstractmethod
    def action_type(self) -> str:
        """Unique identifier for this tool"""
        pass
    
    @abstractmethod
    def get_tool_description(self) -> str:
        """
        Return a description of this tool for the LLM.
        Should explain:
        - What the tool does
        - When to use it
        - Expected input format
        - Expected output format
        """
        pass
    
    @abstractmethod
    def run(self, input_data: Any) -> str:
        """
        Execute the tool with the given input.
        
        Args:
            input_data: The input provided by the agent (could be string, dict, etc.)
        
        Returns:
            String result to be used as Observation
        """
        pass
