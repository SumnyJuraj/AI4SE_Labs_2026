# Prompt 2: Few-Shot Framework (In-Context Exemplar Learning)

**Framework Name:** Few-Shot  
**Source:** [https://frompting.com/frameworks/few-shot](https://frompting.com/frameworks/few-shot)  
**Category:** Communication & Storytelling / Prompt Engineering  
**Application:** Demonstration-Guided Text-to-SQL Translation  

---

### Template Prompt

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
