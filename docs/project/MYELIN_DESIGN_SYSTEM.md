# Myelin UI Design System

A comprehensive guide to the Myelin React Admin Panel design system.

---

## 1. Color Scheme

### Primary Colors (Purple)
| Name | Hex | Usage |
|------|-----|-------|
| Myelin Purple 900 | `#660099` | Deep primary purple (headings, main accent) |
| Myelin Purple 700 | `#7b23a7` | Medium purple (headings, secondary accent) |
| Myelin Purple 200 | `#e8d7ef` | Light lavender tint (hover states, backgrounds) |
| Myelin Purple 50 | `#fbf8fd` | Very light background purple (sidebar background) |

### Secondary Colors
| Name | Hex | Usage |
|------|-----|-------|
| Primary Teal | `#78dcca` | Primary action buttons |
| Secondary Blue | `#32c4ec` | Secondary accent |
| Blue 1 | `#3a84c4` | Standard blue |
| Blue 2 | `#3594ce` | Darker blue variant |
| Orange | `#f49e4c` | Warning/highlight accent |

### Utility Colors
| Name | Hex | Usage |
|------|-----|-------|
| Myelin Dark | `#383838` | Dark gray text |
| Black | `#000000` | Primary text |
| White | `#ffffff` | Backgrounds |
| Success | `#22c55e` | Success states |
| Warning | `#f59e0b` | Warning/caution |
| Danger | `#ef4444` | Destructive actions |
| Border Gray | `#d4d4d8` | Dividers, borders (zinc-300) |

### CSS Variables
```css
:root {
  --myelin-purple-900: #660099;
  --myelin-purple-700: #7b23a7;
  --myelin-purple-200: #e8d7ef;
  --myelin-purple-50: #fbf8fd;
  --primary-teal: #78dcca;
  --secondary-blue: #32c4ec;
  --orange: #f49e4c;
  --myelin-dark: #383838;
}
```

---

## 2. Typography

### Font Families
| Font | Usage | Weights |
|------|-------|---------|
| **Poppins** | Primary sans-serif | 300, 400, 500, 600, 700 |
| **GraviolaSoft** | Page headers and titles | 500 (Medium) |
| **Inter** | Secondary/fallback | System default |

### Font Import
```css
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
```

### Text Sizes
| Element | Size | Weight |
|---------|------|--------|
| Page Headers | 1.5rem (24px) | 600 (semibold) |
| Section Headers | 1.125rem (18px) | 600 (semibold) |
| Body Text | 0.875rem-1rem (14-16px) | 400 (regular) |
| Small/Caption | 0.75rem (12px) | 400-500 |

---

## 3. Button Styles

### Variants
```css
/* Primary Button */
.btn-primary {
  background: linear-gradient(135deg, #78dcca, #32c4ec);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 24px;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-primary:hover {
  opacity: 0.9;
  transform: scale(0.98);
}

/* Secondary Button */
.btn-secondary {
  background: transparent;
  color: #7b23a7;
  border: 2px solid #e8d7ef;
  border-radius: 6px;
  padding: 10px 24px;
  font-weight: 500;
}
.btn-secondary:hover {
  background: rgba(232, 215, 239, 0.5);
}

/* Outline Button */
.btn-outline {
  background: white;
  color: #383838;
  border: 2px solid #d4d4d8;
  border-radius: 6px;
}
.btn-outline:hover {
  border-color: #7b23a7;
}

/* Destructive Button */
.btn-destructive {
  background: #ef4444;
  color: white;
}
```

### Button Sizes
| Size | Height | Padding |
|------|--------|---------|
| xs | 28px | 8px 12px |
| sm | 32px | 8px 16px |
| default | 36px | 10px 24px |
| lg | 40px | 12px 32px |

---

## 4. Card Styles

### Standard Card
```css
.card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 16px;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #383838;
}

.card-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 4px;
}
```

### Myelin Card (Elevated)
```css
.myelin-card {
  background: #f8f9fb;
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgba(156, 163, 175, 0.1),
              0 10px 10px -5px rgba(156, 163, 175, 0.04);
}
```

---

## 5. Table Styles

```css
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.table th {
  background: rgba(212, 212, 216, 0.3);
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #383838;
  border-bottom: 1px solid #d4d4d8;
  border-right: 1px solid #d4d4d8;
}

.table td {
  padding: 12px;
  color: #374151;
  border-right: 1px solid #e5e7eb;
}

/* Alternating row colors */
.table tr:nth-child(odd) {
  background: white;
}
.table tr:nth-child(even) {
  background: #fbf8fd; /* myelin-purple-50 */
}
```

---

## 6. Form Elements

### Input Fields
```css
.input {
  height: 36px;
  padding: 8px 12px;
  border: 1px solid #d4d4d8;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.input:focus {
  outline: none;
  border-color: #7b23a7;
  box-shadow: 0 0 0 3px rgba(123, 35, 167, 0.1);
}

.input::placeholder {
  color: #9ca3af;
}

.input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Labels
```css
.label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #383838;
  margin-bottom: 6px;
  display: block;
}
```

---

## 7. Badge Styles

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-default { background: #78dcca; color: white; }
.badge-success { background: #22c55e; color: white; }
.badge-warning { background: rgba(245, 158, 11, 0.8); color: white; }
.badge-destructive { background: #ef4444; color: white; }
.badge-inactive { background: #d4d4d8; color: white; }
.badge-purple { background: #e8d7ef; color: #7b23a7; }
```

---

## 8. Sidebar Styles

```css
.sidebar {
  width: 275px;
  background: #fbf8fd;
  border-right: 1px solid #d4d4d8;
  height: 100vh;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  color: #71717a;
  border-radius: 6px;
  transition: all 0.2s;
}

.sidebar-item:hover {
  background: #e8d7ef;
  color: #71717a;
}

.sidebar-item.active {
  background: #e8d7ef;
  color: #660099;
  font-weight: 500;
}

.sidebar-item.active .icon {
  color: #660099;
}

.sidebar-item .icon {
  color: #a1a1aa;
  width: 20px;
  height: 20px;
}
```

---

## 9. Header/Navbar Styles

```css
.navbar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  height: 56px;
  padding: 0 20px;
}

.navbar-item {
  color: #4b5563;
  font-weight: 500;
  padding: 8px 16px;
  transition: color 0.2s;
}

.navbar-item:hover {
  color: #3b82f6;
}
```

---

## 10. Shadows & Elevation

```css
/* Light shadow */
.shadow-sm {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Default shadow */
.shadow {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1),
              0 1px 2px rgba(0, 0, 0, 0.06);
}

/* Medium shadow */
.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
              0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* Large shadow (Myelin style) */
.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(156, 163, 175, 0.1),
              0 10px 10px -5px rgba(156, 163, 175, 0.04);
}
```

---

## 11. Spacing System

| Name | Value | Usage |
|------|-------|-------|
| xs | 4px | Tight spacing |
| sm | 8px | Small gaps |
| md | 12px | Default gap |
| lg | 16px | Section spacing |
| xl | 24px | Card padding |
| 2xl | 32px | Large sections |
| 3xl | 48px | Page sections |

---

## 12. Border Radius

| Name | Value | Usage |
|------|-------|-------|
| sm | 4px | Small elements |
| md | 6px | Buttons, inputs |
| lg | 8px | Cards, badges |
| xl | 12px | Large cards |
| full | 9999px | Pills, avatars |

---

## 13. Transitions & Animations

```css
/* Default transition */
.transition {
  transition: all 0.2s ease;
}

/* Smooth transition */
.transition-smooth {
  transition: all 0.3s ease;
}

/* Button press effect */
.btn:active {
  transform: scale(0.95);
}

/* Slide animations */
@keyframes slideDown {
  from { height: 0; opacity: 0; }
  to { height: var(--height); opacity: 1; }
}

@keyframes slideUp {
  from { height: var(--height); opacity: 1; }
  to { height: 0; opacity: 0; }
}
```

---

## 14. Scrollbar Styling

```css
::-webkit-scrollbar {
  width: 6px;
  height: 4px;
}

::-webkit-scrollbar-track {
  background: #e8d7ef;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: rgba(123, 35, 167, 0.3);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #660099;
}
```

---

## 15. Z-Index Layers

| Layer | Z-Index | Usage |
|-------|---------|-------|
| Base | 0 | Default content |
| Dropdown | 10 | Dropdowns, popovers |
| Sticky | 20 | Sticky headers |
| Sidebar | 40 | Mobile sidebar |
| Modal | 50 | Modals, dialogs |
| Toast | 100 | Notifications |

---

## Quick Reference

### Primary Gradient
```css
background: linear-gradient(135deg, #78dcca 0%, #32c4ec 100%);
```

### Purple Gradient
```css
background: linear-gradient(135deg, #7b23a7 0%, #660099 100%);
```

### Focus Ring
```css
box-shadow: 0 0 0 3px rgba(123, 35, 167, 0.2);
```

---

*Design System extracted from Myelin React Admin Panel*
*Location: /myelin-react-admin-panel/src/*
