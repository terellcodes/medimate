from typing import TypedDict, Annotated, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from services.rag_service import retrieve_fda_guidelines, retrieve_predicate_device_details
from config.settings import get_settings
import json


class AgentState(TypedDict):
    """State for the device regulatory agent."""
    messages: Annotated[list, add_messages]


class AnalysisService:
    """Service for analyzing device substantial equivalence."""
    
    def __init__(self):
        self.llm = None
        self.tools = [retrieve_fda_guidelines, retrieve_predicate_device_details]
        self.agent = None
    
    def _get_llm(self):
        """Lazy initialization of LLM."""
        if self.llm is None:
            settings = get_settings()
            self.llm = ChatOpenAI(
                model="gpt-4o-mini", 
                temperature=0,
                openai_api_key=settings.OPENAI_API_KEY
            )
        return self.llm
    
    def _get_agent(self):
        """Lazy initialization of agent."""
        if self.agent is None:
            self.agent = self._create_agent()
        return self.agent
    
    def _create_agent(self):
        """Create the device regulatory agent using LangGraph."""
        # Bind tools to model
        model = self._get_llm().bind_tools(self.tools)
        
        def call_model(state):
            messages = state["messages"]
            response = model.invoke(messages)
            return {"messages": [response]}
        
        def should_continue(state):
            last_message = state["messages"][-1]
            if last_message.tool_calls:
                return "action"
            return END
        
        # Create tool node
        tool_node = ToolNode(self.tools)
        
        # Build graph
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", call_model)
        workflow.add_node("action", tool_node)
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("action", "agent")
        
        return workflow.compile()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the regulatory agent."""
        return """
You are a regulatory agent that determines if a new medical device is substantially equivalent to a predicate device based on FDA 510(k) guidelines.

You have access to:
- `retrieve_fda_guidelines(query)` — FDA guidance on substantial equivalence
- `retrieve_predicate_device_details(query)` — predicate device 510(k) information

**Task:** Compare the new device's indication with the predicate device's indication.

**Process:**
1. Get FDA guidelines on "intended use" and "substantial equivalence" (call this tool 1-2 times)
2. Get predicate device "Indications for Use" (call this tool 1-2 times)
3. Compare and determine equivalence
4. Provide concise analysis

**Important:** After gathering information with tools, provide your final answer. Do not keep calling tools repeatedly.

**Keep responses brief and focused:**
- Reasons: 2-3 short, direct bullet points (under 100 chars each)
- Citations: Most relevant excerpts only (under 200 chars each)
- Suggestions: 1-2 specific, actionable recommendations

**Output format (JSON):**
```json
{
  "substantially_equivalent": <true|false>,
  "reasons": ["Brief reason 1", "Brief reason 2"],
  "citations": [
     {"tool": "fda_guidelines", "text": "Key relevant excerpt"},
     {"tool": "predicate_device", "text": "Key relevant excerpt"}
  ],
  "suggestions": ["Actionable suggestion if not equivalent"]
}
```
"""
    
    async def analyze_device_equivalence(self, new_device_indication: str) -> Dict[str, Any]:
        """Analyze if new device is substantially equivalent to predicate device."""
        try:
            # Create initial state with system prompt and user query
            initial_state = {
                "messages": [
                    SystemMessage(content=self._get_system_prompt()),
                    HumanMessage(content=f"""
New Device — Indications for Use:
"{new_device_indication}"
""")
                ]
            }
            
            # Run the agent with recursion limit
            agent = self._get_agent()
            final_state = await agent.ainvoke(initial_state, config={"recursion_limit": 50})
            
            # Extract the final response
            final_message = final_state["messages"][-1]
            
            # Try to parse JSON response
            try:
                if hasattr(final_message, 'content'):
                    content = final_message.content
                    # Look for JSON in the response
                    if '```json' in content:
                        json_start = content.find('```json') + 7
                        json_end = content.find('```', json_start)
                        json_str = content[json_start:json_end].strip()
                    elif '{' in content and '}' in content:
                        # Find the JSON object in the content
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        json_str = content[start:end]
                    else:
                        json_str = content
                    
                    result = json.loads(json_str)
                    return {
                        "success": True,
                        "analysis": result
                    }
                else:
                    return {
                        "success": False,
                        "error": "No content in agent response",
                        "analysis": None
                    }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse agent response as JSON: {str(e)}",
                    "analysis": {"raw_response": final_message.content if hasattr(final_message, 'content') else str(final_message)}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error during analysis: {str(e)}",
                "analysis": None
            }


# Global instance
analysis_service = AnalysisService()