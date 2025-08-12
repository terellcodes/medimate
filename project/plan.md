# Frontend Implementation Plan for FDA 510(k) Chat Interface

## Overview
Implementation plan for a multi-panel interface featuring device selection, chat interface with workflow pills, and dynamic workspace for FDA 510(k) substantial equivalence process.

## Layout Architecture

```
┌────────┬──────────┬───────────────────┬──────────────┐
│ Device │  Device  │   Chat Interface  │   Workspace  │
│  List  │ Details  │   with Pills      │    Canvas    │
│ Panel  │  Panel   │                   │              │
│        │(Collapsible)                 │              │
└────────┴──────────┴───────────────────┴──────────────┘
```

### Key Components:
1. **Device List Panel** (Leftmost, always visible)
   - Shows list of medical devices
   - Search and filter capabilities
   - Click to select a device

2. **Device Details Panel** (Collapsible, shows when device selected)
   - Slides out when device is selected
   - Shows device specifications, K-number, classification
   - **"New Chat Session" button** - Creates a new analysis session for this device
   - Can be collapsed to save space

3. **Chat Interface** (Main panel with workflow pills)
   - Current chat session for selected device
   - Workflow pills above input box
   - Message history with AI responses

4. **Workspace Canvas** (Right panel for visualizations)
   - Dynamic content based on chat context
   - Shows comparisons, documents, analysis results

## Workflow Pills
Above the chat input, display pills for:
- 🏛️ **Regulatory Pathway** - Guide through 510(k) vs PMA vs De Novo
- 🔍 **Predicate Discovery** - Find suitable predicate devices
- 📋 **IFU Validation** - Validate Instructions for Use

---

## Plan A: Using LlamaIndex Chat-UI

### Tech Stack
- **Framework**: Next.js 15 with App Router
- **Chat UI**: @llamaindex/chat-ui
- **State Management**: Start with useState, add Zustand later if needed
- **Styling**: Tailwind CSS + shadcn/ui components
- **Layout**: react-resizable-panels for panel management
- **Data Fetching**: Start with dummy data, then simple fetch, add React Query later if needed
- **Streaming**: Use built-in streaming from chat-ui library (no WebSockets needed)

### Implementation Steps

#### Phase 1: Setup & Layout (Day 1-2)
```
1. Initialize Next.js project with TypeScript
2. Install core dependencies only:
   - npm install @llamaindex/chat-ui
   - npm install react-resizable-panels
   - npm install tailwindcss @shadcn/ui
3. Create base layout with 4 panels
4. Implement panel resize/collapse logic
5. Use dummy data for all components initially
```

#### Phase 2: Device List Panel (Day 3)
```
1. Create DeviceListPanel component
2. Use dummy device data array
3. Add search/filter functionality (client-side)
4. Handle device selection with useState
5. Style with shadcn/ui components
```

#### Phase 3: Device Details Panel (Day 4)
```
1. Create DeviceDetailsPanel component
2. Implement collapsible animation (CSS transitions)
3. Display device info when selected
4. Add "New Chat Session" button prominently
   - Creates new session object in state
   - Switches chat panel to new session
5. Add quick actions (Analyze, Compare, Export)
6. Use React Context or prop drilling for state
```

#### Phase 4: Chat Interface with LlamaIndex (Day 5-6)
```
1. Integrate @llamaindex/chat-ui components
2. Create custom ChatContainer wrapper
3. Implement workflow pills:
   - Create PillSelector component
   - Define pill actions (use dummy responses for now)
   - Style pills with hover states
4. Configure chat-ui settings:
   - Custom message renderer
   - Use built-in streaming support
   - Mock function calls with dummy data
5. Use dummy API endpoint that returns mock responses
```

#### Phase 5: Workspace Canvas (Day 7-8)
```
1. Create WorkspacePanel component
2. Implement tab navigation:
   - Comparison View
   - Analysis View
   - Document View
3. Add dynamic content loading based on chat context
4. Integrate visualization libraries (recharts)
```

#### Phase 6: State Orchestration (Day 9)
```
1. Create simple orchestration with React Context
2. Implement cross-panel communication:
   - Chat mentions → Workspace updates
   - Device selection → Chat context
   - Pill clicks → Workflow initiation
3. Use local state and prop passing for now
4. Add localStorage for session persistence
```

### File Structure

**What this means**: How to organize your Next.js frontend code files for maintainability and clarity. Each file has a specific purpose.

```
frontend/
├── app/                              # Next.js App Router
│   ├── layout.tsx                   # Root layout with providers
│   ├── page.tsx                     # Main page with 4-panel layout
│   └── api/                         # API route handlers (if needed)
├── components/                       # All React components
│   ├── panels/                      # The 4 main panels
│   │   ├── DeviceListPanel.tsx     # Left panel with device list
│   │   ├── DeviceDetailsPanel.tsx  # Collapsible panel with "New Session" button
│   │   ├── ChatPanel.tsx            # Main chat interface
│   │   └── WorkspacePanel.tsx      # Right panel for visualizations
│   ├── chat/                        # Chat-specific components
│   │   ├── ChatContainer.tsx       # Wraps the chat UI
│   │   ├── PillSelector.tsx        # The 3 workflow pills
│   │   └── MessageRenderer.tsx     # Custom message display
│   └── workspace/                   # Workspace views
│       ├── ComparisonView.tsx      # Compare predicates
│       ├── AnalysisView.tsx        # Show analysis progress
│       └── DocumentView.tsx        # PDF viewer
├── store/                           # State management
│   ├── deviceStore.ts              # Selected device, device list
│   ├── chatStore.ts                # Chat sessions, messages
│   └── orchestrator.ts             # Cross-panel coordination
└── lib/                            # Utility functions
    ├── api.ts                      # API client functions
    └── websocket.ts                # WebSocket connection
```

**Why this structure**:
- **Separation of concerns**: Each component has one job
- **Easy to find files**: Logical grouping by feature
- **Scalable**: Easy to add new panels or views
- **Testable**: Components are isolated

---

## Final Tech Stack (Recommended)

### Core Technologies
- **Framework**: Next.js 15 with App Router
- **Chat UI**: @assistant-ui/react
- **AI Integration**: Vercel AI SDK (ai package)
- **State Management**: Start with useState, add Jotai later if needed
- **Styling**: Tailwind CSS + Radix UI
- **Layout**: Allotment for split panes
- **Data Fetching**: Dummy data first, simple fetch later
- **Streaming**: Vercel AI SDK streaming (no WebSockets needed)

### Implementation Steps

#### Phase 1: Setup & Layout (Day 1-2)
```
1. Initialize Next.js project with TypeScript
2. Install core dependencies:
   - npm install @assistant-ui/react ai
   - npm install allotment
   - npm install @radix-ui/themes
   - npm install lucide-react (for icons)
3. Configure Assistant-UI + Vercel AI SDK providers
4. Create 4-panel layout with Allotment
5. Setup basic streaming chat with dummy tools
```

#### Phase 2: Device Panels (Day 3-4)
```
1. Create device list (no virtual scrolling yet)
2. Implement device details slide-out
   - Collapsible with CSS transitions
   - "New Chat Session" button creates session
   - Shows device specs, K-number, classification
3. Use useState for device state:
   - selectedDevice
   - deviceList (dummy data)
   - deviceDetailsVisible
   - currentSession
4. Add simple search/filter (array.filter)
```

#### Phase 3: Chat Interface with Vercel AI SDK (Day 5-6)
```
1. Create Next.js API route with Vercel AI SDK tools:
   - /api/assistant/route.ts with streamText
   - Define tools for 3 workflow pills
   - Mock FDA analysis responses
2. Implement workflow pills as tool calls:
   - Regulatory Pathway tool
   - Predicate Discovery tool  
   - IFU Validation tool
3. Customize Assistant-UI components:
   - Custom Composer with pills above input
   - Custom Message renderer for tool results
   - Tool UI for FDA data display
4. Connect with useVercelUseAssistantRuntime
```

#### Phase 4: Workspace Integration (Day 7-8)
```
1. Create multi-tab workspace
2. Use assistant-ui's useAssistantContext
3. Implement context-aware views:
   - Listen to tool calls
   - Update based on message content
   - Sync with assistant state
4. Add PDF viewer for documents
```

#### Phase 5: Advanced Features (Day 9-10)
```
1. Implement branching conversations
2. Add voice input with assistant-ui
3. Create custom tool UI components
4. Add collaborative features
5. Implement export functionality
```

### File Structure
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── providers.tsx
│   └── api/
│       └── assistant/
├── components/
│   ├── device/
│   │   ├── DeviceList.tsx
│   │   ├── DeviceDetails.tsx
│   │   └── DeviceSearch.tsx
│   ├── assistant/
│   │   ├── Thread.tsx
│   │   ├── Composer.tsx
│   │   ├── WorkflowPills.tsx
│   │   └── Message.tsx
│   └── workspace/
│       ├── WorkspaceContainer.tsx
│       ├── TabManager.tsx
│       └── views/
├── atoms/
│   ├── deviceAtoms.ts
│   ├── chatAtoms.ts
│   └── workspaceAtoms.ts
└── lib/
    ├── assistant-runtime.ts
    └── fda-tools.ts
```

---

## Data & API Approach

### Phase 1: Dummy Data (Week 1)
Start with hardcoded data in your components. No API calls, no complexity:

```javascript
// In DeviceListPanel.tsx
const DUMMY_DEVICES = [
  { id: 'K123456', name: 'Cardiac Monitor', status: 'cleared' },
  { id: 'K789012', name: 'Blood Pressure Device', status: 'cleared' }
]

// In ChatPanel.tsx
const DUMMY_RESPONSES = {
  'regulatory-pathway': 'Based on your device, 510(k) is the appropriate path...',
  'predicate-discovery': 'I found 3 potential predicates: K111111, K222222...',
  'ifu-validation': 'Your IFU appears complete with all required sections...'
}
```

### Phase 2: Mock API Endpoints (Week 2)
Create Next.js API routes that return dummy data:

```typescript
// app/api/devices/route.ts
export async function GET() {
  return Response.json(DUMMY_DEVICES)
}

// app/api/chat/route.ts
export async function POST(request: Request) {
  const { message } = await request.json()
  
  // Return a streaming response with dummy data
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      const response = "This is a mock response about FDA analysis..."
      for (const word of response.split(' ')) {
        controller.enqueue(encoder.encode(word + ' '))
        await new Promise(r => setTimeout(r, 100)) // Simulate streaming
      }
      controller.close()
    }
  })
  
  return new Response(stream)
}
```

### Phase 3: Real Backend Integration (Week 3+)
Only after the UI is working, connect to real FastAPI backend:

```typescript
// Simply change the API endpoints
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

fetch(`${API_BASE}/api/devices`)  // Now hits FastAPI
```

### Streaming Approach with Vercel AI SDK

Perfect integration between Assistant-UI and Vercel AI SDK:

**Backend (Next.js API Route):**
```typescript
// app/api/assistant/route.ts
import { streamText, tool } from 'ai'
import { z } from 'zod'

export async function POST(req: Request) {
  const { messages } = await req.json()
  
  return streamText({
    model: openai('gpt-4'), // or mock for development
    messages,
    tools: {
      regulatoryPathway: tool({
        description: 'Guide through FDA regulatory pathway',
        parameters: z.object({
          deviceType: z.string(),
        }),
        execute: async ({ deviceType }) => {
          return `For ${deviceType}, 510(k) pathway recommended...`
        }
      }),
      predicateDiscovery: tool({
        description: 'Find suitable predicate devices',
        parameters: z.object({
          deviceDescription: z.string(),
        }),
        execute: async ({ deviceDescription }) => {
          return { predicates: ['K123456', 'K789012'] }
        }
      })
    }
  })
}
```

**Frontend (Assistant-UI):**
```typescript
// Integration is seamless
import { useAssistant } from '@assistant-ui/react'
import { useVercelUseAssistantRuntime } from '@assistant-ui/react'

function ChatPanel() {
  const assistant = useAssistant({ api: '/api/assistant' })
  const runtime = useVercelUseAssistantRuntime(assistant)
  
  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <Thread />
      <WorkflowPills /> {/* Custom pills that trigger tools */}
    </AssistantRuntimeProvider>
  )
}
```

### When to Add Complexity

**Add React Query when:**
- You're fetching the same data in multiple components
- You need background refetching
- You have complex caching requirements

**Add WebSockets when:**
- Multiple users need real-time collaboration
- You need bidirectional real-time updates
- You're building live features (typing indicators, presence)

**Add proper state management (Zustand/Jotai) when:**
- Prop drilling becomes painful (passing through 3+ levels)
- Multiple unrelated components need the same state
- State logic becomes complex

---

## Key Differences Between Plans

### Plan A (LlamaIndex Chat-UI)
**Pros:**
- Simpler integration with existing LlamaIndex backend
- Built-in RAG components
- Good for document-heavy workflows
- Easier function calling setup

**Cons:**
- Less UI customization flexibility
- Limited built-in components
- May need more custom work for pills

### Plan B (Assistant-UI)
**Pros:**
- Modern, highly customizable UI
- Built-in streaming, branching, voice
- Better tool UI integration
- Active development & community

**Cons:**
- Requires Vercel AI SDK backend
- Steeper learning curve
- More complex state management

---

## Recommended Approach

**Assistant-UI + Vercel AI SDK + Next.js** - The optimal combination:
1. **Assistant-UI**: Beautiful, customizable chat components
2. **Vercel AI SDK**: Built-in streaming, function calling, tool integration
3. **Next.js API Routes**: Simple backend endpoints
4. **Perfect Integration**: Designed to work together seamlessly

### Simplified Starting Point

1. **Week 1**: Build UI with dummy data only
   - No API calls
   - No state management libraries
   - Just React useState and props
   - Focus on layout and interactions

2. **Week 2**: Add mock API routes
   - Next.js API routes returning dummy data
   - Simulate streaming responses
   - Test error states

3. **Week 3+**: Integrate real backend
   - Connect to FastAPI
   - Add complexity only as needed
   - Optimize based on real usage

## Next Steps

1. **Review & Approve Plan**: Confirm approach selection
2. **Setup Development Environment**: Initialize project
3. **Create Mock Data**: Device list, chat messages, FDA data
4. **Build Layout Shell**: Get panels working
5. **Implement Core Features**: Follow phase plan
6. **Integrate Backend**: Connect to FastAPI
7. **Test Workflows**: Validate all three pill flows
8. **Polish UI/UX**: Animations, loading states, errors

## Success Criteria

- ✅ All 4 panels render and resize correctly
- ✅ Device selection updates details panel
- ✅ Pills initiate correct workflows
- ✅ Chat and workspace sync bidirectionally
- ✅ FDA data loads and displays properly
- ✅ Export functionality works
- ✅ Mobile responsive (tablet minimum)

## Timeline Estimate

- **Plan A**: 9 working days
- **Plan B**: 10 working days
- **Testing & Polish**: 3 days
- **Total**: ~2.5 weeks