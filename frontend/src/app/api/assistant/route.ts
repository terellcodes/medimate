import { NextRequest } from 'next/server';

// Mock streaming response for development
export async function POST(req: NextRequest) {
  const { messages } = await req.json();
  
  // Get the last message to determine response
  const lastMessage = messages[messages.length - 1];
  const userMessage = lastMessage?.content || '';
  
  // Mock responses based on keywords
  let response = 'I can help you with FDA 510(k) analysis. ';
  
  if (userMessage.toLowerCase().includes('regulatory pathway')) {
    response = `Based on your device characteristics, here's the regulatory pathway analysis:

**Recommended Path: 510(k) Premarket Notification**

1. **Device Classification**: Your device appears to be Class II medical device
2. **Predicate Required**: Yes, you'll need to identify a substantially equivalent predicate
3. **Timeline**: Typically 90-120 days for FDA review
4. **Key Requirements**:
   - Substantial equivalence demonstration
   - Performance testing data
   - Labeling review
   - Quality system requirements

Would you like me to help you find suitable predicate devices next?`;
  } else if (userMessage.toLowerCase().includes('predicate discovery')) {
    response = `I found several potential predicate devices for your analysis:

**Top Predicate Candidates:**

1. **K123456 - Cardiac Monitor System**
   - 95% similarity match
   - Similar intended use
   - Cleared in 2023
   
2. **K789012 - Blood Pressure Monitor** 
   - 87% similarity match
   - Compatible technology
   - Recent clearance

3. **K345678 - Pulse Oximeter**
   - 82% similarity match
   - Similar patient population
   - Well-documented predicate

**Next Steps:**
1. Review detailed comparison for K123456
2. Analyze technological differences
3. Prepare substantial equivalence documentation

Which predicate would you like to analyze first?`;
  } else if (userMessage.toLowerCase().includes('ifu validation')) {
    response = `**IFU (Indications for Use) Validation Results:**

✅ **Validation Status: PASSED**

**Compliance Check:**
- Clear statement of intended use: ✅
- Target patient population defined: ✅
- Clinical conditions specified: ✅
- Contraindications listed: ✅
- Limitations addressed: ✅

**Recommendations:**
1. Consider adding specific age range if applicable
2. Ensure warnings are prominently displayed
3. Include reference to user manual for detailed instructions

**FDA Guidance Compliance:**
Your IFU meets the requirements outlined in:
- FDA Guidance Document: "Format for Traditional and Abbreviated 510(k)s"
- 21 CFR 807.92 requirements

The IFU is ready for submission. Would you like me to generate the complete 510(k) summary document?`;
  } else {
    response = `Hello! I'm your FDA 510(k) analysis assistant. I can help you with:

🏛️ **Regulatory Pathway** - Determine the right path for your device
🔍 **Predicate Discovery** - Find substantially equivalent devices  
📋 **IFU Validation** - Validate your Indications for Use

What would you like to work on today?`;
  }
  
  // Simulate streaming by breaking the response into chunks
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const words = response.split(' ');
      
      for (let i = 0; i < words.length; i++) {
        const chunk = words[i] + (i < words.length - 1 ? ' ' : '');
        controller.enqueue(encoder.encode(chunk));
        
        // Add delay to simulate streaming
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      
      controller.close();
    }
  });
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/plain',
      'Transfer-Encoding': 'chunked',
    },
  });
}