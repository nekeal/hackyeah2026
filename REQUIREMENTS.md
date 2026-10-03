# HackYeah 2026: Kraków Bez Barier - Project Requirements

This document summarizes the core requirements, evaluation criteria, and architectural constraints extracted from the official challenge brief (`KRYTERIA Kraków Bez Barier.pdf`). All AI agents and contributors must ensure their changes are **compliant** with these requirements.

## 1. Core Objective & Scope
- **Goal**: Build a tool (web or mobile app) that helps users assess the accessibility of places and routes based on their *individual* needs.
- **Granular Details**: A simple "accessible/inaccessible" label is **NOT** enough. The app must present detailed information about specific barriers and amenities:
  - Stairs (`highway=steps`)
  - Thresholds/Kerbs (`kerb`)
  - Ramps (`ramp`)
  - Elevators (`elevator`)
  - Entrance widths
  - Surface types (`surface`, `smoothness`)
  - Accessible toilets
  - Resting places
- **Target Audience**: The prototype must focus on a specific target group (e.g., wheelchair users or parents with prams).

## 2. Data & Reliability (CRITICAL)
- **Data Sources**: OpenStreetMap, Open Data portals, crowdsourcing, or business owners. 
- **No Manual City Maintenance**: The solution must NOT require manual database updates by the City of Kraków or access to internal city systems (UMK/MJO).
- **Data Provenance**: For *every* piece of accessibility information, the UI must display:
  - The source of the information (e.g., OSM, User Report).
  - The date of data acquisition or last verification.
  - The reliability status (Verified vs. Unverified).
- **Missing Data Handling**: The application must *never* present a lack of information as a confirmation of accessibility.
- **Data Correction**: The system should provide a mechanism for users to correct invalid or outdated data.

## 3. Technical & Architectural Constraints
- **Separation of Concerns**: The architecture must clearly separate data acquisition and updating (pipelines/services) from data presentation (frontend).
- **Scalability**: The system must be designed so it can be easily deployed in other cities or for private entities (hotels, event organizers).
- **Digital Accessibility (WCAG)**: The User Interface MUST be designed with **WCAG 2.2 AA** compliance in mind. The prototype must support:
  - Keyboard navigation
  - Screen readers
  - Proper contrast ratios
  - Text alternatives for information presented exclusively on the map.

## 4. Evaluation Criteria
When making decisions, prioritize features based on the hackathon scoring weights:
1. **Relevance & Usability** (25%): Does it actually solve the problem for the chosen target group? Is it easy to use?
2. **Business Model & Commercialization** (20%): How will this make money or sustain itself?
3. **Deployment Potential & Scalability** (20%): Can this be easily moved to Warsaw or sold to a hotel chain?
4. **Quality & Completeness of Prototype** (20%): Is the app functional and bug-free?
5. **Data Reliability & Presentation** (15%): Are data sources, dates, and verification statuses clearly visible?

## Compliance Checklist for Agents
Before concluding a feature, verify:
- [ ] Does the UI show the data source and last updated date?
- [ ] Is the data visually separated into verified vs unverified?
- [ ] Are we extracting exact barrier details (not just boolean flags)?
- [ ] Does the UI work with keyboard navigation?
- [ ] Is the backend completely decoupled from the frontend?
