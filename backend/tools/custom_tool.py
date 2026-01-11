"""
Custom Tool Implementation for University AI Assistant
This replaces crewai_tools to avoid dependency issues
"""

import logging
from typing import Callable, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)


class CustomTool(BaseTool):
    """
    Custom tool implementation that works with CrewAI
    Inherits from LangChain's BaseTool for compatibility
    """
    
    name: str
    description: str
    func: Callable = Field(exclude=True)
    
    def __init__(self, name: str, func: Callable, description: str = "", **kwargs):
        super().__init__(
            name=name,
            description=description or func.__doc__ or "No description",
            func=func,
            **kwargs
        )
    
    def _run(self, *args, **kwargs) -> Any:
        """Run method for LangChain/CrewAI compatibility"""
        # Handle both positional and keyword arguments
        if args and not kwargs:
            # If called with positional args, pass them directly
            return self.func(*args)
        elif kwargs and not args:
            # If called with keyword args, pass them directly
            return self.func(**kwargs)
        else:
            # Mixed or no args
            return self.func(*args, **kwargs)
    
    async def _arun(self, *args, **kwargs) -> Any:
        """Async run method (uses sync implementation)"""
        return self._run(*args, **kwargs)


def tool(name: str = None, description: str = None):
    """
    Custom tool decorator that replaces @tool from crewai_tools
    
    Usage:
        @tool(name="My Tool", description="Does something")
        def my_function(param: str) -> str:
            return result
    """
    def decorator(func: Callable) -> CustomTool:
        tool_name = name or func.__name__.replace('_', ' ').title()
        tool_desc = description or func.__doc__ or f"Tool: {tool_name}"
        
        return CustomTool(
            name=tool_name,
            func=func,
            description=tool_desc
        )
    
    # Allow @tool without parentheses
    if callable(name):
        func = name
        return CustomTool(
            name=func.__name__.replace('_', ' ').title(),
            func=func,
            description=func.__doc__ or f"Tool: {func.__name__}"
        )
    
    return decorator
