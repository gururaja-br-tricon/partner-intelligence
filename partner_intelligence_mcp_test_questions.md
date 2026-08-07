# Partner Intelligence MCP Test Questions

This document contains test questions for the Partner Intelligence MCP server.

The questions are designed around the generated partner dataset and cover:
- Company attributes
- Partner capabilities
- Partner program participation
- Partner classification
- Multi-condition partner discovery
- Aggregation and comparison questions
- Multi-step questions that may require multiple MCP calls

## 1. Company Attributes

### Basic partner lookup
1. What are the details of Nexora Technologies?
2. Tell me about partner P001.
3. Which city and state is Nexora Technologies headquartered in?
4. Which country is Nexora Technologies based in?
5. What industry is Nexora Technologies in?
6. How many employees does Nexora Technologies have?
7. What is the annual revenue of Nexora Technologies?
8. When was Nexora Technologies founded?
9. Which partners are currently Active?
10. Which partners are headquartered in Texas?
11. Which partners are headquartered in California?
12. Which partners are headquartered in the USA?
13. Which partners belong to the Information Technology industry?
14. Which partners belong to the Cloud Services industry?

## 2. Capability Questions

### Capability discovery
15. Which partners have AI capabilities?
16. Which partners have Cybersecurity capabilities?
17. Which partners have Cloud capabilities?
18. Which partners have DevOps capabilities?
19. Which partners have Application Modernization capabilities?

### Proficiency
20. Which partners have Expert-level AI capability?
21. Which partners have Advanced-level AI capability?
22. Which partners have Expert-level Cloud capability?
23. Which partners have Advanced-level Cybersecurity capability?
24. Which partners have Expert-level Cybersecurity capability?

### Experience and certifications
25. Which partners have more than 5 years of AI experience?
26. Which partners have more than 5 years of Cybersecurity experience?
27. Which partners have more than 10 AI certifications?
28. Which partners have more than 10 Cybersecurity certifications?
29. Which partners have the highest AI experience?
30. Which partners have the highest number of AI certifications?

## 3. Partner Program Questions

### Vendor participation
31. Which partners participate in the Microsoft partner program?
32. Which partners participate in the AWS Partner Network?
33. Which partners participate in the Google Cloud partner program?

### Partner tier
34. Which partners are Microsoft Gold partners?
35. Which partners are Microsoft Silver partners?
36. Which partners are Microsoft Platinum partners?
37. Which partners are AWS Advanced partners?
38. Which partners have the highest Microsoft partner tier?

### Program details
39. What Microsoft program does Nexora Technologies participate in?
40. What AWS program does Nexora Technologies participate in?
41. What is Nexora Technologies' Microsoft partner tier?
42. When did Nexora Technologies enroll in the Microsoft program?
43. Which partners have been enrolled in Microsoft programs since 2021?
44. Which partners have active Microsoft partnerships?

## 4. Classification Questions

45. Which partners are classified as MSPs?
46. Which partners are classified as System Integrators?
47. Which partners are classified as Consulting Partners?
48. Which partners are classified as Technology Partners?
49. What is Nexora Technologies' primary classification?
50. Which partners have MSP as their primary classification?
51. Which partners have more than one classification?
52. What classifications does Nexora Technologies have?

## 5. Multi-Condition Questions

53. Which partners are headquartered in Texas and have AI capability?
54. Which partners are headquartered in Texas and are Microsoft partners?
55. Which partners are headquartered in Texas and are Microsoft Gold partners?
56. Which partners have Microsoft Gold status and AI capability?
57. Which partners have Microsoft Gold status and Expert AI capability?
58. Which partners have AWS participation and Cybersecurity capability?
59. Which partners have Microsoft participation and Advanced or Expert AI capability?
60. Which MSP partners have Cybersecurity capability?
61. Which MSP partners have AI capability?
62. Which MSP partners are Microsoft Gold partners?
63. Which Texas partners are MSPs?
64. Which Texas partners have AI capability and Microsoft participation?

## 6. High-Value Partner Discovery Questions

65. Find Microsoft Gold partners with Expert AI capability.
66. Find Texas-based Microsoft Gold partners with Expert AI capability.
67. Find Texas-based Microsoft Gold partners with AI capability that are also MSPs.
68. Find AWS partners with Cybersecurity capability.
69. Find MSPs with Advanced or Expert Cybersecurity capability.
70. Find Microsoft partners with Advanced or Expert AI capability.
71. Find active partners in Texas with AI capability.
72. Find active Microsoft Gold partners with AI capability.
73. Find active MSP partners with Cybersecurity capability.
74. Find partners that have both Cloud and AI capabilities.
75. Find partners that have both Cybersecurity and DevOps capabilities.

## 7. Comparison and Ranking Questions

76. Which partner has the most employees?
77. Which partner has the highest annual revenue?
78. Which partner has the most years of AI experience?
79. Which partner has the most AI certifications?
80. Which partners have the strongest AI proficiency?
81. Compare partners with Expert AI capability.
82. Compare Microsoft Gold partners based on their capabilities.
83. Which Texas partner has the strongest AI capability?
84. Which partners have the broadest range of capabilities?
85. Which partners participate in the most partner programs?

## 8. Count / Summary Questions

86. How many partners are in the dataset?
87. How many partners have AI capability?
88. How many partners have Cybersecurity capability?
89. How many partners are Microsoft partners?
90. How many Microsoft Gold partners are there?
91. How many MSP partners are there?
92. How many partners are headquartered in Texas?
93. How many partners have Expert-level capabilities?
94. How many partners participate in both Microsoft and AWS programs?
95. How many partners have both AI and Cybersecurity capabilities?

## 9. Multi-Step / Agent Questions

These questions are especially useful later when the LLM is connected to both Snowflake MCP tools and the PDF/RAG MCP tool.

96. Find Microsoft Gold partners in Texas and summarize their capabilities.
97. Find partners with Expert AI capability and compare their company sizes.
98. Find MSPs with Cybersecurity capability and identify their Microsoft program tier.
99. Find Texas-based Microsoft partners with AI capability and explain their strengths.
100. Find Microsoft Gold partners with Expert AI capability and summarize their company profiles.
101. Find partners with AI and Cybersecurity capabilities and identify their partner classifications.
102. Find AWS partners with Cybersecurity capability and compare their experience.
103. Find Microsoft Gold MSPs and summarize their capabilities.
104. Find the strongest AI partner and explain why based on available partner data.
105. Find Texas-based partners suitable for an AI-focused engagement and explain the selection criteria.

## 10. MCP Parameter Coverage

The current `search_partners` MCP tool exposes these filters:

- `headquarters_state`
- `headquarters_country`
- `industry`
- `status`
- `capability`
- `proficiency_level`
- `vendor`
- `program_name`
- `partner_tier`
- `classification`

The questions above intentionally exercise these filters individually and in combinations.

## 11. Known Demo Scenarios

These scenarios were explicitly validated against the generated dataset:

### Texas + Microsoft Gold + Expert AI
Expected partner:
- P001 — Nexora Technologies

### Texas + Microsoft Gold + AI + MSP
Expected partner:
- P001 — Nexora Technologies

### AWS + Cybersecurity
Expected:
- 3 partners

### Microsoft + Advanced/Expert AI
Expected:
- 5 partners

### MSP + Cybersecurity
Expected:
- 4 partners

## 12. Testing Recommendation

Start with questions 1–20 to validate individual filters.

Then test questions 53–75 to validate multi-condition filtering.

Finally test questions 96–105 to simulate the type of multi-step questions the LLM agent will eventually handle.

For each test, verify:
1. The LLM/tool chooses the correct MCP tool.
2. The MCP tool receives the expected parameters.
3. Snowflake returns the expected partners.
4. The final response does not invent partner attributes that are not present in the data.
