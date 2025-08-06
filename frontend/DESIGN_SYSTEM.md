# Design System Guidelines

## Text Color Standards

To ensure accessibility and readability, use these text color guidelines:

### Primary Text
- **Main headings**: `text-slate-900` (darkest for maximum readability)
- **Body text**: `text-slate-900` (for primary content)
- **Secondary text**: `text-slate-800` (minimum for readability)
- **Helper text**: `text-slate-900` (small text needs higher contrast)

### Avoid These Colors
- ❌ `text-slate-500` - Too light, poor contrast
- ❌ `text-slate-600` - Still too light for body text
- ❌ `text-gray-500` - Same accessibility issues

### Acceptable Light Colors (Use Sparingly)
- `text-slate-800` - Only for secondary information
- `text-slate-700` - Only for disabled states or very large text
- **Avoid lighter colors** - they often fail accessibility tests

### Component-Specific Guidelines

#### Form Elements
- **Labels**: `text-slate-900` with `font-medium`
- **Help text**: `text-slate-900` (small text needs maximum contrast)
- **Placeholders**: Use browser defaults or `text-slate-400`

#### Cards and Containers
- **Card titles**: `text-slate-800`
- **Card content**: `text-slate-800`
- **Meta information**: `text-slate-700`

#### Interactive Elements
- **Button text**: `text-white` on colored backgrounds
- **Link text**: `text-blue-600` or `text-green-600`
- **Hover states**: Darker variants of base color

### Accessibility Testing
- Always test text contrast ratios
- Minimum 4.5:1 for normal text
- Minimum 3:1 for large text (18pt+ or 14pt+ bold)

### Quick Reference
```css
/* Best choices for accessibility */
.text-primary { @apply text-slate-900; }
.text-secondary { @apply text-slate-800; }
.text-muted { @apply text-slate-800; } /* Still readable */

/* Avoid */
.text-light { @apply text-slate-500; } /* Too light! */
.text-medium { @apply text-slate-700; } /* Still too light for small text */
```

## Implementation Checklist
- [ ] Review all existing components for text color compliance
- [ ] Update any `text-slate-500` or `text-slate-600` to darker variants
- [ ] Test with accessibility tools
- [ ] Document any exceptions with justification