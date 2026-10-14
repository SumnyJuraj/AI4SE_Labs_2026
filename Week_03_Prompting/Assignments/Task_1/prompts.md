# Formulated Prompts for Task 2 (Restaurants Text-to-SQL)

This document contains the three formulated prompting frameworks selected for Task 1 and prepared for empirical evaluation in Task 2.

All prompts operate on the `restaurants` SQLite database containing the tables:
- `RESTAURANT (ID, NAME, FOOD_TYPE, CITY_NAME, RATING)`
- `LOCATION (RESTAURANT_ID, HOUSE_NUMBER, STREET_NAME, CITY_NAME)`
- `GEOGRAPHIC (CITY_NAME, COUNTY, REGION)`

---

## 1. Framework: ICIO (Instruction - Context - Input - Output)
- **Framework Type:** Structured Specification / Prompt Engineering
- **Source:** [https://frompting.com/frameworks/icio](https://frompting.com/frameworks/icio)
- **Target File:** [prompt_1_icio.md](file:///home/juraj/skola/zimny1/SIsAI/cviko1/AI4SE_Labs_2026/Week_03_Prompting/Assignments/Task_1/prompt_1_icio.md)

### Template:
```text
[INSTRUCTION]
You are an expert database engineer and SQLite query generator.
Translate the user's natural language question into a valid, executable SQLite query based strictly on the provided database schema.
Rules:
1. When the question asks for the "best" place or restaurant, select LOCATION.HOUSE_NUMBER and RESTAURANT.NAME, and order by RESTAURANT.RATING DESC LIMIT 1.
2. For location, street, or address queries, JOIN RESTAURANT with LOCATION on RESTAURANT.ID = LOCATION.RESTAURANT_ID and select LOCATION.HOUSE_NUMBER, RESTAURANT.NAME.
3. Ignore any conversational distractors or irrelevant musings embedded in the question.
4. Output ONLY the raw SQLite query on a single line. Do not wrap in markdown quotes or code fences. Do not output explanations.

[CONTEXT]
Database Schema:
- RESTAURANT (
    ID INTEGER PRIMARY KEY,
    NAME TEXT,
    FOOD_TYPE TEXT,
    CITY_NAME TEXT,
    RATING REAL
  )
- LOCATION (
    RESTAURANT_ID INTEGER PRIMARY KEY,
    HOUSE_NUMBER INTEGER,
    STREET_NAME TEXT,
    CITY_NAME TEXT
  )
- GEOGRAPHIC (
    CITY_NAME TEXT PRIMARY KEY,
    COUNTY TEXT,
    REGION TEXT
  )

Relationships:
- LOCATION.RESTAURANT_ID references RESTAURANT.ID
- RESTAURANT.CITY_NAME references GEOGRAPHIC.CITY_NAME
- LOCATION.CITY_NAME references GEOGRAPHIC.CITY_NAME

[INPUT]
Question: {question}

[OUTPUT]
```

---

## 2. Framework: Few-Shot Learning (Few-Shot)
- **Framework Type:** Exemplar-based In-Context Learning
- **Source:** [https://frompting.com/frameworks/few-shot](https://frompting.com/frameworks/few-shot)
- **Target File:** [prompt_2_few_shot.md](file:///home/juraj/skola/zimny1/SIsAI/cviko1/AI4SE_Labs_2026/Week_03_Prompting/Assignments/Task_1/prompt_2_few_shot.md)

### Template:
```text
You are a SQLite translator. Convert natural language questions into executable SQLite queries using the following database schema:

Schema:
- RESTAURANT(ID INTEGER PRIMARY KEY, NAME TEXT, FOOD_TYPE TEXT, CITY_NAME TEXT, RATING REAL)
- LOCATION(RESTAURANT_ID INTEGER PRIMARY KEY, HOUSE_NUMBER INTEGER, STREET_NAME TEXT, CITY_NAME TEXT)
- GEOGRAPHIC(CITY_NAME TEXT PRIMARY KEY, COUNTY TEXT, REGION TEXT)
Foreign Key:
- LOCATION.RESTAURANT_ID = RESTAURANT.ID

Guidelines:
- Return ONLY the executable SQLite query on a single line.
- Do not output markdown backticks, explanations, or quotes.

Example 1:
Question: What is the best californian in portola valley ?
SQL: SELECT LOCATION.HOUSE_NUMBER, RESTAURANT.NAME FROM RESTAURANT JOIN LOCATION ON RESTAURANT.ID = LOCATION.RESTAURANT_ID WHERE RESTAURANT.FOOD_TYPE = 'californian' AND LOCATION.CITY_NAME = 'portola valley' ORDER BY RESTAURANT.RATING DESC LIMIT 1;

Example 2:
Question: give me a restaurant on plaza way in lafayette with a rating above 1.8 (poorly rated or better)?
SQL: SELECT LOCATION.HOUSE_NUMBER, RESTAURANT.NAME FROM RESTAURANT JOIN LOCATION ON RESTAURANT.ID = LOCATION.RESTAURANT_ID WHERE LOCATION.STREET_NAME = 'plaza way' AND LOCATION.CITY_NAME = 'lafayette' AND RESTAURANT.RATING > 1.8;

Example 3:
Question: what are some restaurants in vacaville with a rating above 2 (below average or better), while I wonder if dumplings or pancakes could help me find my misplaced umbrella?
SQL: SELECT LOCATION.HOUSE_NUMBER, RESTAURANT.NAME FROM RESTAURANT JOIN LOCATION ON RESTAURANT.ID = LOCATION.RESTAURANT_ID WHERE LOCATION.CITY_NAME = 'vacaville' AND RESTAURANT.RATING > 2;

Example 4:
Question: where can i eat spanish food in oakland ?
SQL: SELECT LOCATION.HOUSE_NUMBER, RESTAURANT.NAME FROM RESTAURANT JOIN LOCATION ON RESTAURANT.ID = LOCATION.RESTAURANT_ID WHERE RESTAURANT.FOOD_TYPE = 'spanish' AND LOCATION.CITY_NAME = 'oakland';

Now convert the following question:
Question: {question}
SQL:
```

---

## 3. Framework: Chain of Thought (CoT)
- **Framework Type:** Step-by-Step Reasoning / Cognitive Decomposition
- **Source:** [https://frompting.com/frameworks/cot](https://frompting.com/frameworks/cot)
- **Target File:** [prompt_3_cot.md](file:///home/juraj/skola/zimny1/SIsAI/cviko1/AI4SE_Labs_2026/Week_03_Prompting/Assignments/Task_1/prompt_3_cot.md)

### Template:
```text
You are an expert SQL engineer. Given the following SQLite database schema:

Schema:
- RESTAURANT(ID INTEGER PRIMARY KEY, NAME TEXT, FOOD_TYPE TEXT, CITY_NAME TEXT, RATING REAL)
- LOCATION(RESTAURANT_ID INTEGER PRIMARY KEY, HOUSE_NUMBER INTEGER, STREET_NAME TEXT, CITY_NAME TEXT)
- GEOGRAPHIC(CITY_NAME TEXT PRIMARY KEY, COUNTY TEXT, REGION TEXT)
Foreign Key:
- LOCATION.RESTAURANT_ID = RESTAURANT.ID

Your task is to translate the user's natural language question into an executable SQLite query by breaking down the problem into explicit reasoning steps.

Solve the following question step by step:
Question: {question}

Step 1 (Intent & Entity Extraction):
- Discard any irrelevant conversational filler, philosophical thoughts, or unrelated food comparisons embedded in the question.
- Identify the requested cuisine / food type, city name, street name, and rating constraints.
- Determine if the user seeks the "best" place (requires sorting by RATING DESC LIMIT 1 and selecting LOCATION.HOUSE_NUMBER, RESTAURANT.NAME) or specific locations (requires selecting LOCATION.HOUSE_NUMBER, RESTAURANT.NAME).

Step 2 (Schema Linking & Joins):
- Identify which tables are needed. If address or street criteria are mentioned, join RESTAURANT and LOCATION on RESTAURANT.ID = LOCATION.RESTAURANT_ID.

Step 3 (SQL Construction):
- Formulate the final valid SQLite query.

Strict Output Format:
Thought: <concise summary of steps 1 to 3 on a single line>
SQL: <single-line executable SQLite query without any markdown code fences or backticks>
```
