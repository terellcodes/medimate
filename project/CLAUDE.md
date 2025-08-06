# 510(k) Agent System Architecture

## Project Goal
Build an AI agent system to automate FDA 510(k) substantial equivalence determination process for regulatory specialists. The system will follow the FDA's 510(k) Decision-Making Flowchart and automate each critical decision point.

## Process Overview

### Step 0: Predicate Discovery (Pre-Decision)
**High-level filtering** to identify potential predicate candidates from FDA databases:
- Basic keyword matching and category filtering
- Regulatory status verification (cleared, not withdrawn/recalled)  
- Document availability confirmation
- Provides pool of candidates for detailed analysis

### Decision Points 1-5: Formal Substantial Equivalence Analysis
**Detailed comparative analysis** following FDA's official 510(k) flowchart:
- **Decision Point 1**: Legal validation of selected predicate device
- **Decision Point 2**: Detailed intended use comparison
- **Decision Point 3**: Detailed technological characteristics comparison  
- **Decision Point 4**: Safety/effectiveness questions analysis
- **Decision Point 5a/5b**: Performance testing methods and data evaluation

## 510(k) Decision-Making Flow

### Step 0: Predicate Device Discovery (Pre-Decision)
**Agent Scope**: Predicate Device Discovery Agent  
*Reference: Pages 10-15, Section IV.C; Page 11 "FDA encourages manufacturers to identify a single predicate device"*

- **Input**: New device characteristics and search parameters
  - Device description keywords
  - Classification regulation/product code (if known)
  - Intended use descriptors
  - Technological characteristics
- **Process**:
  1. **FDA Database Search**: Query FDA endpoints for devices matching keywords
     - Search 510(k) database by device name, classification, product code
     - Filter by cleared devices (not withdrawn/recalled)
     - Retrieve basic device information and 510(k) numbers
  2. **Document Retrieval**: Download 510(k) PDFs for candidate devices
     - Access 510(k) summary documents via FDA API
     - Parse PDF content for device descriptions and intended use
     - Extract technological characteristics from submissions
  3. **Basic Candidate Filtering**: Apply high-level filters to identify viable candidates
     - Verify regulatory status (cleared, not withdrawn/recalled)
     - Confirm document accessibility (510(k) PDF available)
     - Basic device category matching (same general classification)
     - Exclude obvious non-matches (different device class entirely)
  4. **Candidate Prioritization**: Rank candidates for detailed analysis
     - Prioritize by keyword relevance score
     - Consider recency of clearance (more recent = current FDA thinking)
     - Factor in document completeness and quality
     - Limit to top candidates for efficiency (e.g., top 10-20 devices)
- **Output**: Prioritized list of potential predicate candidates ready for detailed analysis
- **Key Considerations**:
  - Focus on discovery and basic filtering, NOT detailed comparison
  - Detailed intended use and technological analysis happens in Decision Points 2-3
  - Provide sufficient candidates to allow for fallback options
  - Balance comprehensiveness with efficiency (avoid analyzing hundreds of devices)

**API Integration Requirements**:
- **openFDA Device 510(k) API**: `https://api.fda.gov/device/510k.json`
  - Search 510(k) submissions by device name, product code, sponsor
  - Access administrative/decision information, receipt dates
  - Covers 1976-present, updated monthly
- **openFDA Device Classification API**: `https://api.fda.gov/device/classification.json`
  - ~1,700 device types across 16 medical specialty panels
  - Device names, product codes, classification levels (I, II, III)
  - Updated monthly
- **openFDA Device Recall API**: `https://api.fda.gov/device/recall.json`
  - Device recall information from 2002-present
  - Updated weekly, identify recalled/withdrawn devices
- **openFDA Device Registration API**: `https://api.fda.gov/device/registrationlisting.json`
  - Device registration and listing information
- PDF processing capabilities for 510(k) document analysis
- Document storage and caching system

### Decision Point 1: Predicate Device Validation
**Agent Scope**: Predicate Device Validator  
*Reference: Pages 10-11, Section IV.C; Page 27, Appendix A Flowchart*

- **Input**: Predicate device identification (510(k) number, PMA number, or classification regulation)
- **Process**: 
  - Verify device is legally marketed per 21 CFR 807.92(a)(3): *Page 10*
    - Pre-May 28, 1976 device OR
    - Reclassified from Class III to Class II/I OR  
    - Found substantially equivalent through 510(k) process
  - Check device hasn't been recalled or removed by FDA per 21 CFR 807.100 *Page 15*
  - Validate predicate device isn't misbranded/adulterated per judicial order
- **Output**: PASS/FAIL + validation details
- **Key Considerations**: 
  - Multiple predicate devices allowed but primary predicate must be identified *Pages 11-12*
  - Split predicates (different devices for intended use vs technology) are NOT allowed *Page 11*
  - Reference devices can be used later but are not predicate devices *Pages 13-14*

### Decision Point 2: Intended Use Analysis  
**Agent Scope**: Intended Use Comparator  
*Reference: Pages 15-18, Section IV.D; Page 16, footnote 21*

- **Input**: New device labeling + predicate device intended use
- **Process**:
  - Extract intended use from proposed labeling per 21 CFR 807.92(a)(5) *Page 16*
  - Compare general purpose/function vs specific indications for use *Page 16*
  - Evaluate if differences create new intended use affecting safety/effectiveness *Pages 17-18*
- **Output**: SAME/DIFFERENT intended use determination
- **Key Considerations**:
  - Only ~10% of NSE decisions are due to new intended use *Page 15*
  - Changes that raise different safety/effectiveness questions = new intended use *Page 17*
  - Tool-type indications (general use) vs disease-specific indications *Page 16*
  - Population changes (adult�pediatric), anatomical changes, clinical context changes *Page 18*

### Decision Point 3: Technological Characteristics Assessment
**Agent Scope**: Technology Comparator  
*Reference: Pages 18-20, Section IV.E; Page 19, footnote 27*

- **Input**: Detailed device descriptions (materials, design, energy source, features)
- **Process**:
  - Compare materials, design, energy source, other device features per Section 513(i)(1)(B) *Page 19*
  - Identify all technological differences *Page 20*
  - Create comparison matrix/table format (FDA recommendation) *Page 20*
- **Output**: SAME/DIFFERENT technological characteristics
- **Required Information** *Pages 19-20*:
  - Overall device design + engineering drawings
  - Materials (chemical formulation, additives, coatings, processing state)
  - Energy sources (delivery method, functional energy affecting patient)  
  - Software/hardware features, density, porosity, degradation characteristics
- **Key Considerations**: Most devices have different technological characteristics from predicate *Page 18*

### Decision Point 4: Safety/Effectiveness Questions Analysis
**Agent Scope**: Risk Assessment Analyzer  
*Reference: Pages 20-22, Section IV.E.3; Pages 21-22, Illustrative Examples*

- **Input**: Technological differences identified in Decision 3
- **Process**:
  - Evaluate if differences raise NEW questions of safety/effectiveness not applicable to predicate *Page 20*
  - Assess if differences pose significant safety/effectiveness concerns
  - Determine if predicate device adequately addresses safety/effectiveness issues
- **Output**: RAISES/DOES NOT RAISE different questions  
- **Key Considerations**: 
  - Rarely results in NSE *Page 18, footnote 26*
  - Must be questions NOT applicable to predicate device *Page 20*
  - Must pose SIGNIFICANT concerns *Page 20*

### Decision Point 5a: Performance Testing Methods Validation
**Agent Scope**: Testing Protocol Validator  
*Reference: Pages 22-23, Section IV.F; Page 22, footnote 32*

- **Input**: Proposed testing methods for addressing technological differences
- **Process**:
  - Evaluate if descriptive information alone is sufficient *Page 22*
  - Assess non-clinical testing appropriateness (bench, biocompatibility, animal studies) *Page 22*
  - Determine if clinical testing required *Page 23*
  - Apply least burdensome approach per FDAMA Section 513(i)(1)(D) *Page 8*
- **Output**: ACCEPTABLE/NOT ACCEPTABLE methods
- **Testing Hierarchy** *Page 22*:
  1. Descriptive information (materials, design, specifications)
  2. Non-clinical bench testing (mechanical, electrical, biological, EMC, sterility, stability, software validation)
  3. Non-clinical animal/biocompatibility studies (GLP compliance required per 21 CFR Part 58)
  4. Clinical studies (<10% of 510(k)s require clinical data) *Page 23*

### Decision Point 5b: Performance Data Evaluation
**Agent Scope**: Data Analysis Validator  
*Reference: Pages 24-26, Section IV.F.1-3; Page 23, footnote 34*

- **Input**: Performance test results and data
- **Process**:
  - Evaluate data against acceptance criteria
  - Compare performance to predicate device benchmarks
  - Assess clinical study results if applicable per valid scientific evidence 21 CFR 860.7(c)(2) *Page 23*
- **Output**: DEMONSTRATES/DOES NOT DEMONSTRATE substantial equivalence
- **Clinical Data Requirements** (when needed) *Pages 24-25*:
  - New/modified indications for use (same intended use)
  - Technological differences requiring clinical validation  
  - Non-clinical methods inadequate/inappropriate
  - IDE compliance for US studies per 21 CFR Part 812 *Page 23, footnote 35*

## Agent System Considerations

### Data Requirements for Each Agent
*Reference: Appendix B, Pages 28-32; Appendix C, Pages 33-38*
- **Device Identification**: 510(k) numbers, classification regulations, product codes
- **Device Descriptions**: Complete technological characterization per 21 CFR 807.92(a)(4) *Page 28*
- **Labeling Information**: Proposed labeling, indications for use statements *Page 29*
- **Performance Data**: Test results, study reports, standards compliance *Pages 30-31*
- **Predicate Information**: Complete predicate device profiles *Page 28*

### Integration Points
- **510(k) Summary Generation**: Automated creation per 21 CFR 807.92 *Pages 26, 28-32*
- **FDA Database Integration**: Access to cleared device database, recall information
- **Standards Database**: Recognition of consensus standards (ASTM, ISO, IEC) *Page 6, footnote 29*
- **Literature Analysis**: Published performance data, adverse event patterns *Page 25*

### Output Generation  
- **Decision Documentation**: Clear rationale for each decision point
- **SE/NSE Determination**: Final substantial equivalence conclusion
- **Deficiency Identification**: Areas requiring additional information/testing *Pages 9-10*
- **Regulatory Pathway Recommendations**: 510(k) continuation vs PMA/De Novo requirements *Pages 9, 15*

### Risk Management
- **FDA Guidance Integration**: Device-specific guidances, special controls *Page 6, footnote 31*
- **Regulatory Updates**: Changes in FDA scientific decision making *Page 25, footnote 37*
- **Quality Controls**: Validation of agent decisions against historical FDA determinations

## Implementation Architecture

### Technical Stack Alignment
- **FastAPI Backend**: Agent orchestration and API endpoints
- **Pydantic Models**: 510(k) data validation and structured outputs
- **Domain-Driven Design**: Separate agents for each decision point
- **Next.js Frontend**: User interface for regulatory specialists
- **Jupyter Notebooks**: Research and validation using 510K document corpus

### Agent Communication Flow
1. User uploads device documentation via frontend
2. FastAPI orchestrates sequential agent execution
3. Each agent validates inputs, processes data, generates outputs
4. Results aggregated into final SE/NSE determination
5. 510(k) summary auto-generated per regulatory requirements