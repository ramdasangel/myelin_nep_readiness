# NEP Readiness Dashboard - Developer Integration Guide

A comprehensive guide for integrating the NEP Readiness Dashboard into your web application.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Integration Methods](#integration-methods)
4. [API Reference](#api-reference)
5. [Data Format](#data-format)
   - [Demo Data Structure (School ABC)](#demo-data-structure-school-abc)
6. [Configuration Options](#configuration-options)
7. [Event Callbacks](#event-callbacks)
8. [Visualizations](#visualizations)
9. [Styling & Customization](#styling--customization)
10. [Responsive Behavior](#responsive-behavior)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The NEP Readiness Dashboard is a self-contained, responsive visualization component for displaying National Education Policy (NEP) 2020 Foundational Philosophy assessment results. It provides:

- **Individual Response Heatmap** - Table view of all respondent scores
- **FP Score Distribution Heatmap** - Matrix heatmap showing score ranges by FP
- **FP Correlation Matrix** - Correlation coefficients between FP dimensions
- **Response Pattern Clusters** - Scatter plot clustering by orientation
- **Statistical summary cards** for each FP dimension
- **Bar, Radar, Doughnut, and Box Plot charts**
- **Leader vs Teacher comparison** views with side-by-side heatmaps
- **Fully responsive** design for desktop, tablet, and mobile
- **Easy API integration** with minimal configuration

### Technology Stack

- **Chart.js** - For charts and visualizations
- **Poppins Font** - Typography (Google Fonts)
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Responsive styles with CSS variables

---

## Quick Start

### Option 1: Direct File Usage

Simply open `nep_dashboard_consolidated.html` in a browser. The demo includes sample data for School ABC with two branches (Branch A and Branch B). Use the branch selector to view:
- **All Branches** - Consolidated data from both branches
- **Branch A** - Data from Branch A only (20 Leaders, 50 Teachers)
- **Branch B** - Data from Branch B only (15 Leaders, 80 Teachers)

### Option 2: Load Your Own Data

```html
<script>
  // After page loads
  NEPDashboard.configure({
    showDemoSelector: false  // Hide demo buttons
  });

  // Load your data
  NEPDashboard.loadData(yourApiResponse);
</script>
```

### Option 3: Fetch from API

```html
<script>
  NEPDashboard.configure({
    token: 'your-jwt-token',
    showDemoSelector: false
  });

  NEPDashboard.loadFromAPI('your-diagnostic-id');
</script>
```

---

## Integration Methods

### Method 1: Standalone HTML Page

Use the dashboard as a standalone page and navigate to it or open in a new tab.

```javascript
// Navigate to dashboard with parameters
window.location.href = 'nep_dashboard_consolidated.html?diagnosticId=YOUR_ID';
```

### Method 2: Iframe Embedding

Embed the dashboard in an iframe for isolation:

```html
<iframe
  id="nep-dashboard"
  src="nep_dashboard_consolidated.html"
  width="100%"
  height="1200"
  frameborder="0">
</iframe>

<script>
  const iframe = document.getElementById('nep-dashboard');

  iframe.onload = function() {
    // Access dashboard API from parent
    const dashboard = iframe.contentWindow.NEPDashboard;

    dashboard.configure({
      showDemoSelector: false
    });

    dashboard.loadData(yourData);
  };
</script>
```

### Method 3: Component Integration

Extract and integrate directly into your application:

1. **Copy the CSS** (inside `<style>` tags) to your stylesheet
2. **Copy the HTML structure** (inside `<body>`) to your template
3. **Copy the JavaScript** (inside `<script>` tags) to your JS file
4. **Include Chart.js** dependency

```html
<!-- Add to your HTML head -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

### Method 4: React/Vue/Angular Integration

Wrap the dashboard in a component:

**React Example:**
```jsx
import { useEffect, useRef } from 'react';

function NEPDashboardWrapper({ data }) {
  const iframeRef = useRef(null);

  useEffect(() => {
    if (iframeRef.current && data) {
      const dashboard = iframeRef.current.contentWindow.NEPDashboard;
      dashboard.configure({ showDemoSelector: false });
      dashboard.loadData(data);
    }
  }, [data]);

  return (
    <iframe
      ref={iframeRef}
      src="/assets/nep_dashboard_consolidated.html"
      style={{ width: '100%', height: '1200px', border: 'none' }}
    />
  );
}
```

---

## API Reference

### `NEPDashboard.configure(options)`

Configure dashboard settings before loading data.

```javascript
NEPDashboard.configure({
  apiBaseUrl: 'https://your-api.com/v1',
  apiEndpoint: '/diagnostics/results',
  token: 'Bearer your-token',
  showDemoSelector: false,
  defaultTab: 'leader',
  onDataLoaded: (data) => { /* callback */ },
  onError: (error) => { /* callback */ },
  onTabChange: (tab) => { /* callback */ }
});
```

**Returns:** `NEPDashboard` (for chaining)

---

### `NEPDashboard.loadFromAPI(diagnosticId, options?)`

Fetch data from a REST API endpoint.

```javascript
// Using configured API
await NEPDashboard.loadFromAPI('diagnostic-123');

// With custom options
await NEPDashboard.loadFromAPI('diagnostic-123', {
  url: 'https://custom-api.com/endpoint',
  token: 'custom-token'
});
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `diagnosticId` | string | The diagnostic assessment ID |
| `options.url` | string | Override API URL |
| `options.token` | string | Override auth token |

**Returns:** `Promise<{ success: boolean, data: object }>`

---

### `NEPDashboard.loadData(apiResponse)`

Load data directly from an object (no API call).

```javascript
const response = {
  status: 0,
  message: 'Success',
  data: {
    diagnostic: { /* ... */ },
    attempts: [ /* ... */ ]
  }
};

NEPDashboard.loadData(response);
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `apiResponse` | object | API response object |

**Returns:** `{ success: boolean, data: object }`

---

### `NEPDashboard.getData()`

Get the current processed data.

```javascript
const data = NEPDashboard.getData();
console.log(data.leader);  // Leader stats
console.log(data.teacher); // Teacher stats
```

**Returns:**
```javascript
{
  leader: {
    processed: [...],  // Individual scores
    stats: { FP1: {...}, FP2: {...}, ... }  // Statistics
  },
  teacher: {
    processed: [...],
    stats: { ... }
  }
}
```

---

### `NEPDashboard.switchTab(tabName)`

Programmatically switch to a tab.

```javascript
NEPDashboard.switchTab('leader');     // Leaders tab
NEPDashboard.switchTab('teacher');    // Teachers tab
NEPDashboard.switchTab('comparison'); // Comparison tab
```

---

### `NEPDashboard.refresh()`

Re-render the dashboard with current data.

```javascript
// Useful after window resize or style changes
NEPDashboard.refresh();
```

---

### `NEPDashboard.destroy()`

Clean up all Chart.js instances. Call before removing the dashboard from DOM.

```javascript
NEPDashboard.destroy();
```

---

## Data Format

### Expected API Response Structure

```json
{
  "status": 0,
  "message": "Success",
  "data": {
    "diagnostic": {
      "diagnosticId": "abc123",
      "diagnosticType": "NEP_READINESS",
      "diagnosticTitle": "School Name - NEP Assessment 2024",
      "setCode": "SCH2024",
      "status": "ACTIVE"
    },
    "attempts": [
      {
        "attemptId": "attempt_001",
        "userId": "user_001",
        "userName": "John Doe",
        "firstName": "John",
        "lastName": "Doe",
        "roleName": "Leader",
        "branchId": "branch_001",
        "branchName": "Main Campus",
        "submittedAt": "2024-01-15T10:00:00.000Z",
        "responses": [
          {
            "questionId": "q1",
            "questionText": "Question text here",
            "responseMetadata": {
              "fpLevel": "3",
              "depthLevel": "2"
            }
          }
        ]
      }
    ],
    "totalAttempts": 50
  }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | number | Yes | `0` for success, non-zero for error |
| `data.diagnostic.diagnosticTitle` | string | Yes | Display title for the assessment |
| `data.attempts` | array | Yes | Array of user attempts |
| `attempts[].userName` | string | Yes | Display name for user |
| `attempts[].roleName` | string | Yes | Must be `"Leader"` or `"Teacher"` |
| `attempts[].responses` | array | Yes | Array of question responses |
| `responses[].responseMetadata.fpLevel` | string | Yes | Value `"1"` to `"5"` |
| `responses[].responseMetadata.depthLevel` | string | No | Value `"1"` to `"4"` |

### Foundational Philosophy (FP) Levels

| Level | Name | Description |
|-------|------|-------------|
| FP1 | Each Child is Unique | Recognizing individual differences |
| FP2 | Holistic & Experiential | Learning through experience |
| FP3 | Reflective Practitioner | Teacher self-reflection |
| FP4 | Assessment for Learning | Formative assessment focus |
| FP5 | Collaboration & Community | Community engagement |

### Demo Data Structure (School ABC)

The demo file includes pre-generated sample data organized as follows:

```
School ABC
├── Branch A (70 respondents)
│   ├── 20 Leaders
│   └── 50 Teachers
│   └── Locations: Main Campus, North Wing, South Wing, East Wing, West Block
│
├── Branch B (95 respondents)
│   ├── 15 Leaders
│   └── 80 Teachers
│   └── Locations: Central Campus, West Campus, Riverside Campus, Hilltop Campus, Valley Wing
│
└── All Branches (165 respondents - consolidated view)
    ├── 35 Leaders total
    └── 130 Teachers total
```

**Data Keys:**
| Key | Description | Data Source |
|-----|-------------|-------------|
| `all` | Consolidated data from both branches | Combined Branch A + Branch B |
| `branch_a` | Branch A data only | School ABC - Branch A |
| `branch_b` | Branch B data only | School ABC - Branch B |

**Using Demo Data Programmatically:**
```javascript
// Access sample data directly
const allData = SAMPLE_DATA.all;        // Consolidated
const branchAData = SAMPLE_DATA.branch_a; // Branch A only
const branchBData = SAMPLE_DATA.branch_b; // Branch B only

// Load specific branch
NEPDashboard.loadData(SAMPLE_DATA.branch_a);
```

**Branch Selector:**
The demo includes a branch selector panel at the top of the dashboard:
- **All Branches** - Shows consolidated data from both branches (default view)
- **Branch A** - Shows only Branch A data
- **Branch B** - Shows only Branch B data

When integrating with your own data, set `showDemoSelector: false` to hide this panel.

---

## Configuration Options

```javascript
NEPDashboard.configure({
  // API Settings
  apiBaseUrl: 'https://api.example.com/v1',
  apiEndpoint: '/diagnostics/get-attempt-results',
  token: 'your-auth-token',

  // UI Settings
  showDemoSelector: true,  // Show/hide branch selector buttons
  defaultTab: 'leader',    // 'leader', 'teacher', or 'comparison'

  // Callbacks
  onDataLoaded: (data) => {
    console.log('Data loaded successfully', data);
  },
  onError: (error) => {
    console.error('Dashboard error', error);
    showErrorToast(error.message);
  },
  onTabChange: (tab) => {
    analytics.track('dashboard_tab_change', { tab });
  }
});
```

---

## Event Callbacks

### onDataLoaded

Fired when data is successfully loaded and rendered.

```javascript
NEPDashboard.configure({
  onDataLoaded: (data) => {
    console.log('Diagnostic:', data.diagnostic);
    console.log('Leaders:', data.leaderCount);
    console.log('Teachers:', data.teacherCount);
    console.log('Processed Data:', data.currentData);
  }
});
```

### onError

Fired when an error occurs during data loading.

```javascript
NEPDashboard.configure({
  onError: (error) => {
    // Show user-friendly error
    alert('Failed to load dashboard: ' + error.message);

    // Log for debugging
    console.error('Dashboard Error:', error);
  }
});
```

### onTabChange

Fired when user switches tabs.

```javascript
NEPDashboard.configure({
  onTabChange: (tab) => {
    // Track analytics
    gtag('event', 'view_tab', { tab_name: tab });

    // Update URL hash
    window.location.hash = tab;
  }
});
```

---

## Visualizations

The dashboard includes multiple visualization types organized by tab:

### Leaders & Teachers Tabs

Each tab displays the following visualizations:

| Chart | Type | Description |
|-------|------|-------------|
| **Summary Cards** | Stat Cards | Average score for each FP (FP1-FP5) with color coding |
| **Individual Response Heatmap** | Table | Scrollable table showing each respondent's FP scores with color intensity |
| **Average FP Scores** | Bar Chart | Horizontal bar chart comparing average scores across FPs |
| **FP Profile (Radar)** | Radar Chart | Pentagon-shaped chart showing FP distribution pattern |
| **Dominant FP Distribution** | Doughnut Chart | Shows which FP each respondent is most aligned with |
| **Score Range (Box Plot)** | Stacked Bar | Displays min, Q1, median, Q3, max distribution for each FP |
| **FP Score Distribution Heatmap** | Matrix Table | 5x5 matrix showing respondent counts by FP and score range (0-3, 4-6, 7-9, 10-12, 13-15) |
| **Response Pattern Clusters** | Scatter Plot | Clusters respondents by Child-Centric (FP1+FP2) vs Practice-Oriented (FP3+FP4+FP5) orientation |
| **FP Correlation Matrix** | Matrix Table | Shows Pearson correlation coefficients between all FP pairs (-1 to +1) |

### Comparison Tab

| Chart | Type | Description |
|-------|------|-------------|
| **Average FP Scores** | Grouped Bar Chart | Side-by-side comparison of Leaders vs Teachers |
| **FP Profile Overlay** | Radar Chart | Overlaid radar showing both Leader and Teacher profiles |
| **Score Distribution Heatmap Comparison** | Dual Matrix | Side-by-side heatmaps for Leaders (purple) and Teachers (teal) |
| **Dominant FP - Leaders** | Doughnut Chart | Leader FP dominance distribution |
| **Dominant FP - Teachers** | Doughnut Chart | Teacher FP dominance distribution |
| **Response Pattern Clusters** | Scatter Plot | Combined cluster view with Leaders (circles) and Teachers (triangles) |

### Color Coding

**FP Colors:**
| FP | Color | Hex |
|----|-------|-----|
| FP1 | Purple | #7b23a7 |
| FP2 | Teal | #0d9488 |
| FP3 | Blue | #0284c7 |
| FP4 | Orange | #d97706 |
| FP5 | Violet | #7c3aed |

**Role Colors:**
| Role | Color | Hex |
|------|-------|-----|
| Leaders | Purple | #7b23a7 |
| Teachers | Teal | #0d9488 |

**Heatmap Scales:**
- **Score Heatmap:** Gray → Light Purple → Purple (low to high count)
- **Correlation Matrix:** Red (-1) → Gray (0) → Green (+1)

---

## Styling & Customization

### CSS Variables

Override these CSS variables to customize colors:

```css
:root {
  /* Primary Purple Palette */
  --myelin-purple-900: #660099;
  --myelin-purple-700: #7b23a7;
  --myelin-purple-200: #e8d7ef;
  --myelin-purple-50: #fbf8fd;

  /* Accent Colors */
  --primary-teal: #78dcca;
  --secondary-blue: #32c4ec;
  --orange: #f49e4c;

  /* Text Colors */
  --myelin-dark: #383838;

  /* Role Colors */
  --leader-color: #7b23a7;
  --teacher-color: #0d9488;
}
```

### Custom Styling Example

```css
/* Make header blue instead of purple */
.header {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
}

/* Change stat card colors */
.stat-card.fp1 {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
}

/* Customize fonts */
body {
  font-family: 'Your-Font', sans-serif !important;
}

/* Customize matrix heatmap */
.matrix-table td.heat-cell {
  border-radius: 4px;
}
```

---

## Responsive Behavior

The dashboard automatically adapts to different screen sizes with optimized layouts for each breakpoint:

| Breakpoint | Screen Size | Layout Changes |
|------------|-------------|----------------|
| **> 1400px** | Large Desktop | Full layout, 5-column stats, 2-column comparison heatmaps |
| **1200-1399px** | Desktop | Single-column cards, scrollable matrices |
| **992-1199px** | Tablet Landscape | Compact stats, single-column comparison heatmaps |
| **768-991px** | Tablet Portrait | 3-column stats, stacked cards, smaller fonts |
| **576-767px** | Mobile Landscape | 2-column stats, vertical tabs, horizontal scroll on matrices |
| **< 576px** | Mobile Portrait | Compact fonts (0.65rem), touch-friendly spacing |
| **< 400px** | Small Mobile | Minimal fonts (0.5rem), hidden sublabels |

### Touch Device Enhancements

- Minimum 44px touch targets for buttons and interactive elements
- Smooth scrolling with `-webkit-overflow-scrolling: touch`
- Active state feedback on matrix cells

### Landscape Mode

- Optimized layouts for mobile landscape orientation
- Reduced header/padding for more content visibility
- Side-by-side comparison heatmaps restored

### Forcing Refresh on Resize

```javascript
window.addEventListener('resize', debounce(() => {
  NEPDashboard.refresh();
}, 250));
```

---

## Troubleshooting

### Charts Not Rendering

**Cause:** Chart.js not loaded before dashboard initialization.

**Solution:**
```html
<!-- Load Chart.js BEFORE the dashboard -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### CORS Errors

**Cause:** API doesn't allow cross-origin requests.

**Solution:**
- Configure CORS on your API server
- Use a proxy server
- Or load data server-side and pass to dashboard

### Data Not Showing

**Cause:** Invalid data format or missing required fields.

**Solution:** Validate your data structure:
```javascript
// Check required fields
console.log('Status:', response.status);  // Should be 0
console.log('Attempts:', response.data?.attempts?.length);
console.log('First attempt roleName:', response.data?.attempts?.[0]?.roleName);
```

### Iframe Communication Issues

**Cause:** Cross-origin iframe restrictions.

**Solution:** Ensure same-origin or use postMessage:
```javascript
// Parent window
iframe.contentWindow.postMessage({ type: 'loadData', data: myData }, '*');

// Inside dashboard (add this listener)
window.addEventListener('message', (event) => {
  if (event.data.type === 'loadData') {
    NEPDashboard.loadData(event.data.data);
  }
});
```

### Memory Leaks

**Cause:** Charts not destroyed when removing dashboard.

**Solution:** Always call destroy before removal:
```javascript
NEPDashboard.destroy();
dashboardElement.remove();
```

### Heatmap Not Scrolling on Mobile

**Cause:** Touch scrolling not enabled.

**Solution:** The dashboard includes `-webkit-overflow-scrolling: touch` by default. If issues persist, ensure parent containers don't have `overflow: hidden`.

### Charts Overlapping

**Cause:** Container sizing issues.

**Solution:** Ensure the iframe or container has sufficient height (minimum 1200px recommended for full dashboard).

---

## Example: Full Integration

```html
<!DOCTYPE html>
<html>
<head>
  <title>My App - NEP Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <div id="app">
    <h1>Assessment Results</h1>
    <iframe id="dashboard-frame" src="nep_dashboard_consolidated.html"
            style="width:100%; height:1200px; border:none;"></iframe>
  </div>

  <script>
    const iframe = document.getElementById('dashboard-frame');

    iframe.onload = async function() {
      const dashboard = iframe.contentWindow.NEPDashboard;

      // Configure
      dashboard.configure({
        showDemoSelector: false,
        onDataLoaded: (data) => {
          console.log('Loaded:', data.leaderCount, 'leaders,', data.teacherCount, 'teachers');
        },
        onError: (err) => alert('Error: ' + err.message)
      });

      // Fetch your data
      const response = await fetch('/api/diagnostics/results', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ diagnosticId: 'your-id' })
      });

      const data = await response.json();

      // Load into dashboard
      dashboard.loadData(data);
    };
  </script>
</body>
</html>
```

---

## Support

For issues or questions:
- Check the browser console for error messages
- Validate your API response format
- Ensure all required fields are present
- Test with the built-in demo data first (All Branches / Branch A / Branch B buttons)

---

*Last Updated: January 2026*
*Version: 2.1.0*
