# AI Agent & RAG Prototype Development Guide

This directory serves as a prototyping environment for building AI agents and RAG (Retrieval Augmented Generation) applications using Python notebooks. This guide outlines proven strategies and patterns for rapidly developing and testing AI-powered systems before production implementation.

## Core Development Philosophy

**Notebook-First Approach**: Use Jupyter notebooks to rapidly prototype, experiment, and validate AI agent architectures before implementing in production code. This allows for iterative development, visual debugging, and easy experimentation with different approaches.

## Essential Setup Patterns

### Environment Configuration
```python
import os
import getpass

# API Keys Management
os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API Key:")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "ProjectName"
os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your Langsmith API Key:")
```

### Core Dependencies Structure
```python
# Vector Store & Embeddings
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# Document Processing
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Agent Framework
from langgraph.graph import StateGraph
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
```

## Vector Store Strategies

### Dual Namespace Architecture
Create separate collections for different data types to enable targeted retrieval:

```python
# Guidelines/Reference Data
guidelines_client.create_collection(
    collection_name="guidelines",
    vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
)

# Domain-Specific Documents
domain_client.create_collection(
    collection_name="domain_docs",
    vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
)
```

### Document Processing Pipeline
1. **Loading**: Use appropriate loaders for different file types
2. **Chunking**: Apply text splitting with optimal chunk sizes and overlap
3. **Embedding**: Generate embeddings with consistent models
4. **Storage**: Store in named collections for organized retrieval

## RAG Tool Development

### Tool Creation Pattern
```python
@tool
def retrieve_domain_knowledge(
    query: Annotated[str, "query description"]
):
    """Tool description for the agent"""
    return retriever.invoke(query)
```

### Multi-Source Retrieval Strategy
- **Reference Tools**: Access authoritative guidelines, standards, or documentation
- **Domain Tools**: Query specific documents relevant to the use case
- **External Tools**: Integrate web search or external APIs when needed

## Agent Architecture Patterns

### State-Based Agent Design
```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    # Add domain-specific state fields as needed
```

### LangGraph Implementation Strategy
1. **Node Definition**: Create distinct nodes for different agent capabilities
2. **Flow Control**: Use conditional edges to manage execution paths  
3. **Tool Integration**: Bind tools to models for function calling
4. **State Management**: Track conversation and context through state

### Prompt Engineering Approach
- **System Prompts**: Define agent role, capabilities, and constraints
- **Task Flow**: Specify step-by-step execution logic
- **Output Format**: Define structured response schemas
- **Error Handling**: Include fallback behaviors and validation rules

## Testing & Validation Strategies

### Iterative Query Testing
```python
# Test with various input scenarios
test_queries = [
    "Basic functionality test",
    "Edge case scenario",
    "Complex multi-step request"
]

for query in test_queries:
    result = agent.invoke(create_initial_state(query))
    # Analyze and validate results
```

### Stream-Based Debugging
```python
async for chunk in agent.astream(input, stream_mode="updates"):
    for node, values in chunk.items():
        print(f"Node: {node}")
        print(f"Output: {values}")
```

## Common Agent Patterns

### Analysis Agent Pattern
- **Information Gathering**: Use multiple retrievers to collect relevant context
- **Comparative Analysis**: Compare new inputs against existing knowledge
- **Structured Output**: Return formatted analysis with reasoning and citations
- **Recommendation Engine**: Provide actionable suggestions based on analysis

### Multi-Tool Orchestration
- **Sequential Tool Use**: Chain tool calls for complex workflows
- **Parallel Processing**: Use multiple tools simultaneously when appropriate
- **Context Preservation**: Maintain context across tool invocations
- **Error Recovery**: Handle tool failures gracefully

### Domain-Specific Specialization
- **Expert System Behavior**: Encode domain expertise in prompts and tool selection
- **Compliance Checking**: Validate outputs against domain standards
- **Citation Management**: Track and reference source materials
- **Quality Assurance**: Implement validation checks for output quality

## Optimization Techniques

### Performance Optimization
- **Embedding Caching**: Reuse embeddings for repeated queries
- **Retrieval Tuning**: Optimize search parameters (k-values, similarity thresholds)
- **Tool Selection**: Choose appropriate tools based on query characteristics
- **Response Caching**: Cache responses for identical queries

### Accuracy Improvement
- **Multi-Stage Retrieval**: Use multiple retrieval rounds for complex queries
- **Context Enhancement**: Enrich context with metadata and structured information
- **Validation Loops**: Implement self-checking mechanisms
- **Human-in-the-Loop**: Design for human validation and feedback

## Production Readiness

### Validation Checklist
- [ ] Agent handles edge cases gracefully
- [ ] Tool calls are efficient and reliable
- [ ] Output format is consistent and structured
- [ ] Error handling covers common failure modes
- [ ] Performance meets requirements under load

### Migration Strategy
1. **Extract Core Logic**: Identify reusable components from notebook
2. **Service Architecture**: Design production service structure
3. **API Design**: Define clean interfaces for agent interactions
4. **Testing Framework**: Create comprehensive test suites
5. **Monitoring**: Implement observability and performance tracking

## Best Practices

### Development Workflow
1. **Start Simple**: Begin with basic RAG before adding complexity
2. **Iterate Rapidly**: Use notebooks for quick experimentation
3. **Test Thoroughly**: Validate with diverse input scenarios
4. **Document Decisions**: Record architectural choices and trade-offs
5. **Plan Migration**: Consider production requirements from the start

### Code Organization
- **Modular Functions**: Break complex logic into reusable functions
- **Clear Naming**: Use descriptive names for tools, nodes, and variables
- **Comment Key Decisions**: Explain non-obvious implementation choices
- **Version Control**: Track notebook changes and experiment results

## Productionization Prompt Template

Once your prototype is complete and validated in the notebook, use this prompt template to guide Claude Code in building the production system:

### Generic Productionization Prompt

```
We will be productionizing the prototype found in ./notebooks/[NOTEBOOK_NAME].ipynb including an API and UI.

From now on "notebook" refers to ./notebooks/[NOTEBOOK_NAME].ipynb

Task 1: UI
- A: Top Menu Bar
    - Include Logo for the App: [APP_NAME]
    - [Additional header elements as needed]
- B: Main Content
    - A Hero Banner describing what the product does:
        - Catchphrase that captures the core value proposition
        - Detailed but engaging description in smaller text
    - A row of [NUMBER] cards describing the key features
    - A "Try Now" button which scrolls down to the functional UI
    - Functional UI Components:
        - [Document/Data upload component matching your prototype's input method]
        - Once upload complete, provide a summary including:
            - [List the key extracted fields from your document processing]
        - Input component for [primary user input - text box, form, etc.]
        - Submit button to process the input
        - Results section to display output from your AI agent

Task 2: API
- A: RAG Infrastructure
    - Single vector store with multiple namespaces
    - On startup, load [reference documents/guidelines] into vector store as seen in notebook
    - Support loading user documents into separate namespace
- B: Document Processing Endpoint
    - Create upload endpoint: upload_[DOCUMENT_TYPE]
    - Process uploaded documents (chunking, embedding, storage) like the notebook
    - Return structured extraction results
- C: AI Agent Endpoint
    - Create analysis endpoint that accepts [primary input parameters]
    - Run the [AGENT_NAME] found in the notebook
    - Leverage vector stores from Tasks 2A and 2B
    - Return structured analysis results

Architecture Requirements:
- Use FastAPI for backend with proper error handling
- Use [FRONTEND_FRAMEWORK] for frontend
- Implement proper logging and monitoring
- Follow the patterns established in the notebook for:
    - Vector store management (dual namespace approach)
    - Tool creation and RAG retrieval
    - Agent state management and execution
    - Structured output formatting

Performance Requirements:
- Efficient document processing pipeline
- Responsive UI with loading states
- Proper error handling for failed uploads/processing
- Scalable vector store operations
```

### Customization Guidelines

**Replace these placeholders with your specific values:**
- `[NOTEBOOK_NAME]`: Your prototype notebook filename
- `[APP_NAME]`: Your application name
- `[NUMBER]`: Number of feature cards you want
- `[Document/Data upload component]`: Specific to your use case (PDF upload, CSV import, etc.)
- `[Key extracted fields]`: The specific fields your document processing extracts
- `[Primary user input]`: The main input users provide (text, structured data, etc.)
- `[DOCUMENT_TYPE]`: Type of documents you're processing (pdf, csv, json, etc.)
- `[AGENT_NAME]`: The name of your agent variable in the notebook
- `[Primary input parameters]`: The parameters your agent endpoint accepts
- `[FRONTEND_FRAMEWORK]`: React, Vue, Angular, etc.

**Customize these sections based on your domain:**
- Add domain-specific validation requirements
- Include any specialized processing steps
- Specify compliance or security requirements
- Add integration requirements for external services

This framework provides a solid foundation for building sophisticated AI agents and RAG applications. The notebook environment enables rapid prototyping while maintaining a clear path to production implementation.