# Chat Interface Design for FDA 510(k) Substantial Equivalence Process

## Overview

This document outlines the design and implementation strategy for a split-view chat interface to guide users through the iterative FDA 510(k) substantial equivalence determination process. The interface features a conversational AI assistant on the left panel and a dynamic workspace on the right panel for interactive data exploration and analysis.

## Core User Experience Vision

### The Iterative Nature of 510(k) Process

The FDA substantial equivalence process is inherently iterative:
1. **Discovery**: Search for potential predicate devices
2. **Analysis**: Evaluate each predicate through Decision Points 1-5
3. **Iteration**: If a predicate fails, try another candidate
4. **Documentation**: Track all attempts and generate reports

A chat interface naturally supports this "try, fail, learn, try again" pattern while maintaining context across attempts.

## Architecture Overview

### Split-View Layout

```
┌─────────────────────────────────────────────────────────┐
│                    Application Header                     │
├──────────────────────┬───────────────────────────────────┤
│                      │                                   │
│                      │                                   │
│    Chat Interface    │         Workspace                 │
│                      │                                   │
│  - Conversation      │  - Dynamic Components             │
│  - Rich Messages     │  - Predicate Details              │
│  - Embedded Cards    │  - Comparison Tables              │
│  - Action Buttons    │  - PDF Viewers                    │
│                      │  - Analysis Results               │
│                      │                                   │
└──────────────────────┴───────────────────────────────────┘
```

## Technology Stack

### Frontend Libraries

#### Layout & State Management
- **Allotment** or **React Resizable Panels**: Resizable split-pane layout
- **Jotai** or **Zustand**: Global state management for cross-panel communication
- **TanStack Query**: Server state management and caching for FDA data
- **React Router** or **TanStack Router**: Workspace navigation and deep linking

#### Chat Panel (Left)
- **Vercel AI SDK**: Streaming responses, function calling, `useChat` hook
- **react-markdown**: Render formatted FDA guidance and explanations
- **react-syntax-highlighter**: Display code/data snippets
- **framer-motion**: Smooth animations for message appearance
- **cmdk**: Command palette for power users (`/compare`, `/restart`, `/export`)

#### Workspace Panel (Right)
- **@tanstack/react-table**: Interactive comparison tables for predicates
- **react-pdf**: Display and navigate 510(k) PDF documents
- **recharts** or **tremor**: Data visualizations for analysis results
- **react-hook-form**: Complex forms for device information input
- **react-tabs** or custom tabs: Navigate between workspace views

### Backend Integration
- **FastAPI + WebSockets**: Real-time updates during analysis
- **LangChain** or **LlamaIndex**: Orchestrate AI agents for each decision point
- **PostgreSQL + Prisma**: Store conversation history and analysis results
- **Redis**: Cache FDA API responses and session state

## Chat Interface Features

### Progressive Information Gathering

Instead of overwhelming users with complex forms, the chat naturally builds the device profile through conversation:

```typescript
// Example conversation flow
User: "I need to find a predicate for my cardiac monitor"
AI: "I'll help you find a suitable predicate. Does your device have therapeutic features or is it monitoring-only?"
User: "It has arrhythmia detection and alerts"
AI: "Got it. Let me search for cardiac monitors with similar therapeutic claims..."
[Workspace updates with search results]
```

### Smart Entity Recognition

The chat automatically detects and highlights FDA-specific entities:

```typescript
const entityPatterns = {
  predicates: /K\d{6}/g,              // K123456
  classifications: /21 CFR \d+\.\d+/g, // 21 CFR 870.2700
  productCodes: /[A-Z]{3}/g,           // DQA, MGB
  decisionPoints: /Decision Point [1-5]/gi,
  fdaGuidance: /FDA-\d{2}-[A-Z]-\d+/g
}
```

### Rich Message Components

Embed interactive components directly in chat messages:

```jsx
// Hybrid chat message with embedded component
<ChatMessage>
  <Text>I found 3 potential predicates that match your criteria:</Text>
  <PredicateComparisonCard predicates={[...]} />
  <ActionButtons>
    <Button onClick={() => analyze('K123456')}>Analyze K123456</Button>
    <Button onClick={() => showMore()}>Show More Options</Button>
  </ActionButtons>
</ChatMessage>
```

### Contextual Commands

Power users can use slash commands for quick actions:
- `/compare K123456 K789012` - Compare two predicates
- `/restart` - Start fresh analysis
- `/export` - Generate FDA-ready documentation
- `/history` - View all attempted predicates
- `/help` - Show available commands

## Workspace Features

### Dynamic Content Based on Chat Context

The workspace automatically updates based on the conversation:

```typescript
interface WorkspaceState {
  activeView: 'search' | 'comparison' | 'analysis' | 'documents'
  activePredicates: string[]
  comparisonMode: boolean
  decisionPoint: 1 | 2 | 3 | 4 | 5 | null
  pinnedDocuments: Document[]
}
```

### Workspace Views

#### 1. Search View
- Filter and sort predicate candidates
- Visual cards with key device information
- Quick actions: "Compare", "Analyze", "View PDF"

#### 2. Comparison View
- Side-by-side predicate comparison
- Highlight differences in intended use and technology
- Export comparison as PDF/Excel

#### 3. Analysis View
- Current decision point progress
- Pass/fail indicators with explanations
- Suggested next actions

#### 4. Documents View
- PDF viewer for 510(k) submissions
- Highlighted relevant sections
- Annotation capabilities

## Orchestration Layer

### Bidirectional Communication

The orchestration layer manages state synchronization between chat and workspace:

```typescript
// Central orchestrator using Jotai atoms
const orchestratorAtoms = {
  activePredicateAtom: atom<string | null>(null),
  comparisonModeAtom: atom<boolean>(false),
  workspaceTabAtom: atom<WorkspaceTab>('search'),
  analysisSessionAtom: atom<AnalysisSession | null>(null),
  mentionedEntitiesAtom: atom<Entity[]>([])
}
```

### Event Flow Examples

#### Chat → Workspace
```typescript
// User mentions a predicate in chat
chatMessage: "Let's analyze K123456"
↓
Parser extracts: { action: 'ANALYZE', predicateId: 'K123456' }
↓
Workspace updates:
- Switch to analysis tab
- Load K123456 details
- Start Decision Point 1 validation
- Show loading indicator
```

#### Workspace → Chat
```typescript
// User clicks "Try Different Predicate" in workspace
workspaceAction: { type: 'SELECT_PREDICATE', id: 'K789012' }
↓
Chat receives event
↓
Chat responds: "I see you've selected K789012. This device has similar 
intended use but different technology. Let me run the validation..."
```

### State Synchronization Patterns

```typescript
// Custom hook for orchestration
function useOrchestrator() {
  const [activePredicate, setActivePredicate] = useAtom(activePredicateAtom)
  const [workspaceTab, setWorkspaceTab] = useAtom(workspaceTabAtom)
  
  // Parse chat messages for entities and actions
  const processChatMessage = useCallback((message: string) => {
    const entities = extractEntities(message)
    const action = inferAction(message)
    
    // Update workspace based on chat context
    if (entities.predicates.length > 0) {
      setActivePredicate(entities.predicates[0])
      if (action === 'COMPARE') {
        setWorkspaceTab('comparison')
      } else if (action === 'ANALYZE') {
        setWorkspaceTab('analysis')
      }
    }
  }, [])
  
  // Handle workspace interactions
  const handleWorkspaceAction = useCallback((action: WorkspaceAction) => {
    // Update chat context based on workspace
    if (action.type === 'PREDICATE_SELECTED') {
      appendChatMessage({
        role: 'system',
        content: `User selected predicate ${action.predicateId} from workspace`
      })
    }
  }, [])
  
  return { processChatMessage, handleWorkspaceAction }
}
```

## Implementation Phases

### Phase 1: Core Infrastructure
- Set up split-view layout with resizable panels
- Implement basic chat interface with streaming
- Create workspace tab navigation
- Establish state management with Jotai

### Phase 2: Entity Recognition & Linking
- Implement FDA entity parser
- Add entity highlighting in chat
- Create click-to-load functionality
- Build predicate search interface

### Phase 3: Dynamic Workspace
- Implement comparison table component
- Add PDF viewer integration
- Create analysis progress tracking
- Build decision point visualization

### Phase 4: Advanced Features
- Add conversation branching/saving
- Implement export functionality
- Create collaboration features
- Add voice input support

## User Journey Examples

### Successful Path
```
1. User: "I need a predicate for my blood pressure monitor"
2. AI: Searches and displays candidates in workspace
3. User: Selects K123456 from workspace
4. AI: Runs validation, shows progress in workspace
5. All decision points pass
6. AI: "Great! K123456 is substantially equivalent. Here's your report..."
7. Workspace: Shows exportable 510(k) summary
```

### Iteration Path
```
1. User: "Check if K111111 works for my device"
2. AI: Starts validation process
3. Decision Point 2 fails (different intended use)
4. AI: "K111111 won't work due to intended use differences. Based on the 
       failure, K222222 might be better - it has similar therapeutic claims"
5. Workspace: Updates with K222222 comparison
6. User: "Yes, try that one"
7. AI: Continues with new predicate
```

## Key Design Principles

### 1. Progressive Disclosure
- Start simple, reveal complexity as needed
- Don't overwhelm with all options upfront
- Guide users through the process step-by-step

### 2. Maintain Context
- Remember all attempted predicates
- Show why previous attempts failed
- Learn from failures to suggest better options

### 3. Bidirectional Interaction
- Chat actions update workspace
- Workspace interactions inform chat
- Neither panel blocks the other

### 4. Expert Assistance
- AI acts as regulatory consultant
- Explains FDA requirements in plain language
- Suggests next best actions based on context

### 5. Audit Trail
- Track all decisions and attempts
- Generate FDA-compliant documentation
- Maintain conversation history for compliance

## Success Metrics

- **Time to Decision**: Reduce from days to hours
- **Iteration Efficiency**: Find suitable predicate in fewer attempts
- **User Confidence**: Clear explanations at each step
- **Compliance Rate**: Generated documents meet FDA requirements
- **User Adoption**: Intuitive enough for non-experts

## Future Enhancements

- **Multi-user Collaboration**: Team members contribute to analysis
- **ML-Powered Suggestions**: Learn from successful predicates
- **Regulatory Updates**: Auto-incorporate new FDA guidance
- **Integration Hub**: Connect to internal PLM/QMS systems
- **Mobile Experience**: Review and approve on mobile devices