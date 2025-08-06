# Recall/Safety Checking Implementation Plan

## Goal
Add recall/safety verification to prevent suggesting recalled devices as predicates for Step 0 Predicate Discovery.

## Current State
- ✅ Product code search implemented
- ✅ Combined search functionality working
- ❌ No recall/safety verification

## Recall/Safety Requirements Analysis

### What We Need to Check
1. **Device Recall Status** - Has the device been recalled?
2. **Recall Classification** - Class I (most serious) to Class III
3. **Recall Status** - Ongoing, Completed, Terminated
4. **Device Withdrawal** - Has FDA withdrawn clearance?
5. **Safety Alerts** - Any ongoing safety concerns

### OpenFDA Recall API Details
- **Endpoint**: `https://api.fda.gov/device/recall.json`
- **Coverage**: 2002 to present, updated weekly
- **Search Fields**: `device_name`, `manufacturer`, `product_code`, `k_number`

## Implementation Strategy

### Option A: Reactive Filtering (Recommended)
```python
def check_device_safety(k_number, device_name, manufacturer):
    # Search recall database for this specific device
    # Filter out if any active recalls found
    # Simple binary: Safe = use as predicate, Not safe = exclude
    return True/False
```

### Option B: Proactive Safety Scoring
```python
def score_device_safety(device_info):
    # Check recalls, assign safety score
    # Include recalled devices but flag them
    # More complex but gives users choice
    return safety_score, recall_details
```

## Integration Points

### In Current Workflow
1. **After device discovery** - Check each found device
2. **Before PDF download** - Don't waste time on recalled devices
3. **In device metadata** - Add safety status fields

### New Fields to Add
```python
device_metadata = {
    # ... existing fields
    'safety_status': 'safe|recalled|withdrawn',
    'recall_info': {
        'has_recalls': True/False,
        'recall_count': int,
        'most_recent_recall': date,
        'highest_recall_class': 'I|II|III'
    }
}
```

## Technical Approach

### Simple Implementation (MVP)
1. Add `check_recalls()` function
2. Call it for each device in main loop
3. Add boolean `is_safe_predicate` flag
4. Filter out unsafe devices from downloads
5. Show safety status in device listing

### API Query Strategy
```python
# Search by K-number (most specific)
recall_query = f'k_number:"{k_number}"'

# Fallback: search by device name + manufacturer
recall_query = f'product_description:"{device_name}" AND firm_name:"{manufacturer}"'
```

## User Experience

### CLI Options
```bash
# Default: Filter out recalled devices
uv run python fetch_510k_pdf.py --product-code "DYB"

# Include recalled devices but show warnings  
uv run python fetch_510k_pdf.py --product-code "DYB" --include-recalled

# Show only safety information
uv run python fetch_510k_pdf.py --product-code "DYB" --safety-check-only
```

### Output Enhancement
```
📋 ALL DEVICES FOUND (10):
  1. ✅ HeartSpan Steerable Sheath (SAFE)
  2. ⚠️  Old Cardiac Catheter (RECALLED - Class II)
  3. ❌ Defective Device (RECALLED - Class I)
```

## Implementation Priority

### Phase 1: Basic Safety Filter
1. Add recall API integration
2. Binary safe/unsafe filtering
3. Update device metadata
4. Test with known recalled devices

### Phase 2: Enhanced Safety Info  
5. Add recall classification details
6. Add CLI options for recalled devices
7. Improve safety status display

## Questions to Resolve

### Critical Decisions
1. **Should we exclude ALL recalled devices or just Class I/II?**
   - Recommendation: Exclude Class I (most dangerous), warn on Class II/III
2. **What about old recalls that are "completed"?**
   - Recommendation: Still exclude - completed doesn't mean safe to use as predicate
3. **Should we check recalls by K-number or device name?**
   - Recommendation: Try K-number first, fallback to device name + manufacturer
4. **How to handle API failures - fail safe or fail open?**
   - Recommendation: Fail safe - if can't verify safety, don't recommend as predicate

### Technical Considerations
- **Performance**: Batch recall checks if possible
- **Rate Limiting**: Recall API has same limits as 510(k) API
- **Caching**: Cache recall results to avoid repeated API calls
- **Error Handling**: Graceful degradation when recall API unavailable

## Success Criteria
- Zero recalled devices appear in predicate recommendations by default
- Clear safety warnings for any flagged devices  
- No false positives (safe devices marked as recalled)
- Fast execution (safety check doesn't slow down search significantly)
- Users can override safety filtering if needed (with clear warnings)

## Example Implementation Flow
```python
# In main device processing loop
for device in api_data['results']:
    device_info = extract_device_info(device)
    
    # NEW: Safety check
    safety_result = check_device_recalls(device_info)
    device_info['safety_status'] = safety_result['status']
    device_info['recall_info'] = safety_result['details']
    
    # Skip recalled devices unless --include-recalled flag
    if safety_result['status'] == 'recalled' and not include_recalled:
        logger.warning(f"Skipping {device_info['k_number']} - device has been recalled")
        continue
    
    # Continue with existing logic...
```

## Testing Strategy
- Test with known recalled devices from FDA database
- Verify safe devices aren't incorrectly flagged
- Test API failure scenarios
- Performance testing with large device lists
- Validate recall classification mapping

## Future Enhancements
- Integration with FDA warning letters database
- Medical device reporting (MDR) adverse event checking
- Real-time safety alert subscriptions
- Safety scoring algorithm based on multiple factors