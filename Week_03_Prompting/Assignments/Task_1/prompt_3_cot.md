# Prompt 3: CoT Framework (Chain of Thought Reasoning)

**Framework Name:** Chain of Thought (CoT)  
**Source:** [https://frompting.com/frameworks/cot](https://frompting.com/frameworks/cot)  
**Category:** Reasoning & Analysis  
**Application:** Step-by-Step Entity Extraction and Query Synthesis  

---

### Template Prompt

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
