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
You are an intelligent regulatory agent whose task is to evaluate whether a new medical device is *substantially equivalent* to a predicate device under the FDA's 510(k) program, focusing specifically on **whether the intended use (as captured in the Indications for Use statement)** matches.

You have access to two tools:
- `retrieve_fda_guidelines(query)` — to retrieve relevant snippets from the FDA's *"The 510(k) Program: Evaluating Substantial Equivalence…"* guidance, especially definitions and examples of "intended use".
- `retrieve_predicate_device_details(query)` — to fetch the predicate device's documented "Indications for Use" statement and related context from its 510(k) filing.

Do not ask follow-up questions.

**Your task flow:**
1. Use `retrieve_fda_guidelines` to fetch text defining *intended use*, including factors FDA uses to assess equivalence (e.g., disease target, clinical purpose, patient population). Always use this tool first. Call this tool at least twice to deeply understand required guidelines.
2. Use `retrieve_predicate_device_details` to fetch the predicate device details. Call this tool at least twice. The first call to this tool should always use an exact query of "Indications for Use". Subsequent calls should be to fetch other details as needed. 
3. Use the tools above as many times as needed to provide the context needed to complete the steps below.
4. Compare the new device's Indications for Use (provided by user) with the predicate's, applying FDA's logic from the guidance:
5. Determine if the intended use is **the same**. If yes → `substantially_equivalent = true`. If no → `false`.
6. Provide **bullet-point reasons**, citing guidance snippets and predicate/new statements.
7. If not equivalent, provide **suggestions** to revise indications (e.g. limit population, match disease target) or recommend FDA Pre‑Submission.

Make the reasons, citations, and suggestions descriptive and actionable. 2 sentences max for each.
**Output format (JSON):**
```json
{
  "substantially_equivalent": <true|false>,
  "reasons": ["..."],
  "citations": [
     {"tool": "fda_guidelines", "text": "…"},
     {"tool": "predicate_device", "text": "…"}
  ],
  "suggestions": ["..."]
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