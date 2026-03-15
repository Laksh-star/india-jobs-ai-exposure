# AI Exposure of the Indian Job Market

This document packages the current India adaptation of `karpathy/jobs`.
It uses NCO 2004 3-digit groups as the canonical occupation unit and a blended approximation strategy: seed labour-market estimates, bundled AI exposure scores, and seed demand proxies shaped around the planned PLFS + NCS pipeline.

## Summary

- Occupation groups in bundle: 28
- Workers represented in bundle: 441,200,000
- Job-weighted AI exposure: 3.2/10

## Highest-demand digital and business groups

| Occupation | NCO 2004 | Workers | Monthly earnings | Demand index | Exposure |
|------------|----------|---------|------------------|--------------|----------|
| Computing Professionals | 213 | 5.2M | INR 58,000 | 89 | 9/10 |
| Computer Associate Professionals | 312 | 1.7M | INR 36,000 | 82 | 8/10 |
| Business Professionals | 241 | 8.8M | INR 47,000 | 76 | 8/10 |
| Architects, Engineers and Related Professionals | 214 | 7.4M | INR 52,000 | 71 | 7/10 |
| Client Information Clerks | 422 | 6.7M | INR 23,000 | 68 | 7/10 |
| Health Professionals (except nursing) | 222 | 2.1M | INR 68,000 | 65 | 5/10 |
| Shop Salespersons and Demonstrators | 522 | 27.0M | INR 19,000 | 63 | 6/10 |
| Motor Vehicle Drivers | 832 | 16.8M | INR 24,000 | 61 | 4/10 |
| Nursing Professionals | 223 | 3.4M | INR 32,000 | 59 | 4/10 |
| Electrical and Electronic Equipment Mechanics and Fitters | 724 | 4.9M | INR 30,000 | 58 | 5/10 |

## All bundled occupation groups

| Occupation | Category | Workers | Demand | Exposure | Rationale |
|------------|----------|---------|--------|----------|-----------|
| Agricultural, Fishery and Related Labourers | agriculture | 78.0M | 12 | 1/10 | The work is overwhelmingly manual, local, and low-cost, so AI exposure is minimal. |
| Market-Oriented Crop and Animal Producers | agriculture | 57.0M | 18 | 2/10 | AI will mainly augment planning and advisory layers while leaving the core production work largely intact. |
| Labourers in Mining, Construction, Manufacturing and Transport | manual-labour | 46.5M | 24 | 2/10 | AI changes coordination around the job more than the core labor itself, so direct exposure remains low. |
| Market Gardeners and Crop Growers | agriculture | 42.0M | 19 | 2/10 | AI can guide crop decisions but cannot cheaply replace large amounts of physical farm work in Indian conditions. |
| Sales and Service Elementary Occupations | elementary-service | 29.4M | 33 | 3/10 | This group remains low exposure because much of the work is informal, physical, and tightly linked to local presence. |
| Shop Salespersons and Demonstrators | retail | 27.0M | 63 | 6/10 | Digital selling tools and automated recommendations will compress parts of the role, but a large in-person component remains. |
| Market-Oriented Animal Producers and Related Workers | agriculture | 18.5M | 23 | 2/10 | The occupation remains low exposure because the physical care tasks dominate and the economics favor augmentation over replacement. |
| Motor Vehicle Drivers | transport | 16.8M | 61 | 4/10 | AI will change routing and dispatch systems a lot, but the actual driving task remains only moderately exposed in India. |
| Textile, Garment and Related Trades Workers | manufacturing | 13.2M | 42 | 5/10 | The work is repetitive enough to face automation pressure, but labor-cost economics and physical handling keep exposure moderate. |
| Building Frame and Related Trades Workers | construction | 11.4M | 38 | 2/10 | The work is highly physical and site-specific, so AI exposure remains low. |
| House Keeping and Restaurant Services Workers | hospitality | 9.6M | 52 | 3/10 | The administrative layer can be digitized, but the core service work still depends on physical presence and human interaction. |
| Building Finishers and Related Trades Workers | construction | 9.3M | 36 | 3/10 | AI affects estimation and supervision more than the hands-on finishing work, so exposure stays low to moderate. |
| Other Teaching Professionals | education | 9.1M | 47 | 6/10 | AI will reshape content creation and assessment heavily, but live teaching, student management, and trust still require human presence. |
| Business Professionals | business | 8.8M | 76 | 8/10 | Core outputs are text, spreadsheets, and analysis, so AI can automate or compress a significant portion of daily work. |
| Numerical Clerks | clerical | 8.3M | 57 | 8/10 | Routine numerical processing and document-driven bookkeeping are among the most compressible office workflows. |
| Architects, Engineers and Related Professionals | engineering | 7.4M | 71 | 7/10 | AI can speed up analysis and documentation substantially, but engineering work still carries physical-world, safety, and regulatory constraints. |
| Machinery Mechanics and Fitters | industrial-trades | 6.8M | 46 | 4/10 | AI will improve diagnosis and maintenance planning, but the occupation still depends heavily on physical repair work. |
| Client Information Clerks | service-office | 6.7M | 68 | 7/10 | A large part of first-line customer communication is structured and scriptable, making this group highly exposed. |
| Secretaries and Keyboard-Operating Clerks | clerical | 5.9M | 44 | 8/10 | The occupation is highly exposed because much of the work is routine digital coordination and document handling. |
| Computing Professionals | digital | 5.2M | 89 | 9/10 | This is one of the most exposed occupation groups because core tasks are digital, decomposable, and already seeing large productivity gains from AI. |
| Personal Care Workers | care | 5.2M | 50 | 3/10 | This group has low exposure because the value comes from physical, relational, and continuous human care. |
| Electrical and Electronic Equipment Mechanics and Fitters | industrial-trades | 4.9M | 58 | 5/10 | Compared with purely mechanical trades, the digital diagnostic layer is larger, but the occupation still cannot be done entirely from a computer. |
| Food and Related Products Machine Operators | manufacturing | 3.5M | 41 | 4/10 | Exposure is moderate because plant automation can advance, but the work still includes manual materials handling and shift-floor response. |
| Nursing Professionals | healthcare | 3.4M | 59 | 4/10 | Nursing is only moderately exposed because AI helps the paperwork and monitoring layers, not the physical and interpersonal core of the occupation. |
| Other Department Managers | management | 2.6M | 48 | 6/10 | The work contains a large digital coordination component, but execution still depends on human supervision, escalation handling, and relationships. |
| Health Professionals (except nursing) | healthcare | 2.1M | 65 | 5/10 | AI will be highly useful in the information-processing parts of the job, but core care decisions and patient-facing work remain only moderately exposed. |
| Computer Associate Professionals | digital | 1.7M | 82 | 8/10 | The role is not as exposed as software engineering, but a large share of repetitive troubleshooting and documentation is automatable. |
| Directors and Chief Executives | management | 900K | 34 | 7/10 | AI will compress analysis, planning, and coordination layers around this role, but final accountability and organizational leadership remain human-intensive. |