# Healthcare Analytics Dashboard

## Overview

The Agentic Healthcare Analytics Platform includes a real-time interactive dashboard built in React, visualising all agent outputs in a single unified view.

## Live Dashboard Features

### Tab 1 — Overview
- **8 KPI cards**: Total patients, readmission rate, high-risk count, anomalies, avg age, avg LOS, avg medications, avg glucose
- **Risk distribution pie chart**: High / Medium / Low breakdown
- **Patients by diagnosis bar chart**: horizontal bar per diagnosis group
- **Age distribution histogram**: patient population spread
- **Top 5 predictive features**: feature importance bar chart from Random Forest model

### Tab 2 — Patient Table
- All 25 patients sorted by risk score (highest first)
- Colour-coded vitals: glucose and systolic BP turn amber/red when elevated
- Risk badge: colour-coded Low / Medium / High with percentage
- Click any row to expand full clinical detail panel

### Tab 3 — Anomalies
- 4 summary cards: total anomalies, tachycardia count, high BP count, extended stays
- Flagged patient list with emoji severity icons (🚨 Critical, ⚠️ Warning)
- Clinical flag tags per patient (e.g. TACHYCARDIA, HIGH BP, EXTENDED STAY)

### Tab 4 — Run Agents
- 4 agent cards showing pipeline stages
- **Execute Full Agent Pipeline** button
- Live animated console output showing each agent running in real time
- Completion status per agent

## Technology

- **React** with hooks (`useState`, `useEffect`)
- **Recharts** for all charts (PieChart, BarChart, ResponsiveContainer)
- **Tailwind CSS** (via inline styles for artifact compatibility)
- Dark theme: Navy `#0A1628` base with Teal `#0D9488` accents

## Solix Integration Path

In production, this dashboard would connect to:
- **Solix AI Healthcare HIMS** — live patient risk feed
- **Solix Common Data Platform** — real-time KPI metrics
- **Solix ECS** — report generation triggers
- **FHIR R4** — patient data via Integration Hub

## Running Locally

The dashboard is available as `healthcare_dashboard.jsx` — a single-file React component.

To embed in a Next.js or CRA project:

```bash
npm install recharts
```

```jsx
import Dashboard from './healthcare_dashboard.jsx'
export default function App() { return <Dashboard /> }
```

## Screenshots

The dashboard features:
- Dark clinical aesthetic (navy/teal/amber palette)
- IBM Plex Mono monospace font for data density
- Colour-coded risk indicators
- Animated agent console for live pipeline execution
