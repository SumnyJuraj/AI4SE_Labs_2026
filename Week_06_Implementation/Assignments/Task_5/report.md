# Technical Report: RAG-Driven Automated Code Synthesis & Unit Test Verification

**Course:** AI for Software Engineering (AI4SE)  
**Lab:** Week 06 – Implementation  
**Assignment:** Task 5 – End-to-End RAG Coding Pipeline & Verification  
**Pipeline Script:** [rag_pipeline.py](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_5/rag_pipeline.py)  
**Test Results Data:** [test_results.json](file:///home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_5/test_results.json)  
**Selected Model:** `gpt-4o-mini` (from the authorized model pool)  
**Target Repository:** `AI4SE_Playground`  

---

## 1. Executive Summary & Benchmark Result

In Task 5, we assembled the complete Retrieval-Augmented Generation (RAG) agent pipeline connecting:
1. The **Context-Enriched AST Chunks** from Task 2.
2. The **Vector Embeddings Storage** from Task 3 (`BAAI/bge-small-en-v1.5`, 384 dimensions).
3. The **Top-N Vector Matching Engine** from Task 4 (Cosine Similarity).
4. An **LLM Code Synthesis Engine** utilizing the authorized `gpt-4o-mini` model.
5. An **Automated AST Code Injector** that surgically replaces target methods in source files.

The pipeline was executed across all 10 missing methods specified in `missing_code.json`. After code synthesis, the full unit test suite was executed:

| Test Metric | Initial Baseline (Unimplemented) | Post-RAG Pipeline (Synthesized) |
|---|:---:|:---:|
| **Total Test Cases** | 481 | **481** |
| **Passing Tests** | 429 | **481** |
| **Failing Tests** | 35 | **0** |
| **Erroring Tests** | 17 | **0** |
| **Pass Rate** | 89.19% | **100.0% (ALL GREEN)** |
| **Execution Duration** | 0.089s | **0.158s** |

---

## 2. End-to-End RAG Pipeline Architecture

```mermaid
sequenceDiagram
    autonumber
    actor Driver as Pipeline Runner
    participant Task as Task Input (missing_code.json)
    participant Matcher as Task 4 Matcher (fastembed)
    participant LLM as OpenAI Chat API (gpt-4o-mini)
    participant Injector as AST Code Injector
    participant Target as Source Files (.py)
    participant Tester as Unittest Suite (481 Tests)

    Driver->>Task: Load task specification (File, Class, Method, Docstring)
    Task->>Matcher: Query: target_file + class + method + docstring
    Matcher->>Matcher: Compute query embedding & cosine similarity
    Matcher-->>Driver: Return Top 5 Context Chunks (Classes, Tests, Types)
    Driver->>LLM: Prompt with Task Specification + 5 Retrieved Context Chunks
    LLM-->>Driver: Synthesized Python Method Implementation
    Driver->>Injector: Inspect target file AST; locate method boundaries
    Injector->>Target: Safely replace method block & validate syntax (ast.parse)
    Driver->>Tester: Execute python3 -m unittest discover -s tests
    Tester-->>Driver: 481/481 Tests Passed (100% Green)
```

### Key Technical Innovations in the Pipeline

1. **Dual Context Ingestion (Source + Specification Tests):**  
   Because our chunking in Task 2 and embedding in Task 3 indexed both `playground/playground/` (source) and `playground/tests/` (test cases), the matcher retrieved both the enclosing class context AND the exact unit test suite defining the method's behavior.
2. **Context-Aware Syntactic Inferences:**  
   - For `OrderStatus.is_terminal`, the retrieved test `assertIs(OrderStatus.SHIPPED.is_terminal, True)` informed the LLM to generate a `@property` rather than an ordinary callable method.
   - For `Money.__bool__` and `Order.__len__`, the pipeline enforced standard dunder method rules (never `@property`).
   - For `BulkDiscountPricing.price`, the retrieved `FlatPricing` and `PricingStrategy` chunks informed the LLM to delegate to `self._base.price(items)` and calculate discounts using `.cents`.
3. **AST-Guided In-Place Replacement:**  
   The injector does not perform naive regex replacement. It parses the target file into a Python AST, extracts the exact `lineno` to `end_lineno` range of the existing stub, cleans LLM markdown fences, re-indents to match the class body (4 spaces), and validates that the modified file compiles cleanly before writing to disk.

---

## 3. Implementation Summary for All 10 Missing Methods

| Task # | Target Class & Method | Source File | Top 1 Chunk | Implemented Logic | Result |
|---|---|---|---|---|:---:|
| **1** | `OrderStatus.is_terminal` | `enums.py` | `cls_0007` | `@property` returning `self in (OrderStatus.SHIPPED, OrderStatus.CANCELLED)` | **PASS** |
| **2** | `InventoryLedger.__contains__` | `inventory.py` | `cls_0016` | Normalizes SKU safely with `try/except (ValueError, TypeError)`; checks `normalized in self._on_hand` | **PASS** |
| **3** | `Warehouse.stock_report` | `inventory.py` | `cls_0016` | Dict comprehension `{sku: self._ledger.available(sku) for sku in sorted(self._ledger) if available > 0}` | **PASS** |
| **4** | `OrderStateMachine.transition` | `orders.py` | `cls_0023` | Validates `self.can_transition(source, target)`; raises `InvalidTransitionError(source, target)` on failure | **PASS** |
| **5** | `OrderLog.by_status` | `orders.py` | `cls_0026` | Generator generator yielding `order for order in self if order.status == status` | **PASS** |
| **6** | `Customer.can_afford` | `models.py` | `cls_0022` | Validates `self.balance + total <= self.credit_limit` | **PASS** |
| **7** | `Order.__len__` | `orders.py` | `cls_0088` | Returns `len(self.items)` representing the number of line items | **PASS** |
| **8** | `BulkDiscountPricing.price` | `pricing.py` | `cls_0028` | Computes `base = self._base.price(items)`; applies floor discount `(base.cents * self._percent_off) // 100` if quantity $\ge$ threshold | **PASS** |
| **9** | `EventBus.__contains__` | `events.py` | `cls_0009` | Checks `event_type in self._subscribers and bool(self._subscribers[event_type])` | **PASS** |
| **10** | `Money.__bool__` | `models.py` | `mth_0019` | Evaluates boolean truthiness: `return self._cents != 0` | **PASS** |

---

## 4. Synthesized Code Artifacts

Below are the actual method implementations synthesized by `gpt-4o-mini` and written into the codebase:

````carousel
```python
# Task 1: playground/enums.py -> OrderStatus.is_terminal
@property
def is_terminal(self) -> bool:
    """True when the status ends further transitions."""
    return self in (OrderStatus.SHIPPED, OrderStatus.CANCELLED)
```
<!-- slide -->
```python
# Task 2: playground/inventory.py -> InventoryLedger.__contains__
def __contains__(self, sku: object) -> bool:
    """Return whether sku normalises to a SKU with positive on-hand stock."""
    if not isinstance(sku, str):
        return False
    try:
        normalized_sku = normalize_sku(sku)
        return normalized_sku in self._on_hand
    except (ValueError, TypeError):
        return False
```
<!-- slide -->
```python
# Task 3: playground/inventory.py -> Warehouse.stock_report
def stock_report(self) -> Dict[str, int]:
    """Return a mapping of SKU to available quantity."""
    return {
        sku: self._ledger.available(sku)
        for sku in self._ledger
        if self._ledger.available(sku) > 0
    }
```
<!-- slide -->
```python
# Task 4: playground/orders.py -> OrderStateMachine.transition
def transition(self, source: OrderStatus, target: OrderStatus) -> OrderStatus:
    """Return target if the transition is allowed, else raise."""
    if not self.can_transition(source, target):
        raise InvalidTransitionError(source, target)
    return target
```
<!-- slide -->
```python
# Task 5: playground/orders.py -> OrderLog.by_status
def by_status(self, status: OrderStatus) -> Iterator[Order]:
    """Yield orders whose status matches status."""
    for order in self:
        if order.status == status:
            yield order
```
<!-- slide -->
```python
# Task 6: playground/models.py -> Customer.can_afford
def can_afford(self, total: Money) -> bool:
    """Return True if balance + total does not exceed the credit limit."""
    if not isinstance(total, Money):
        raise TypeError("total must be Money")
    return (self.balance + total) <= self.credit_limit
```
<!-- slide -->
```python
# Task 7: playground/orders.py -> Order.__len__
def __len__(self) -> int:
    """Return the number of line items."""
    return len(self.items)
```
<!-- slide -->
```python
# Task 8: playground/pricing.py -> BulkDiscountPricing.price
def price(self, items: Sequence[LineItem]) -> Money:
    """Return the base price, less the discount if the quantity qualifies."""
    base_total = self._base.price(items)
    total_quantity = sum(item.quantity for item in items)
    if total_quantity >= self._threshold:
        discount_cents = (base_total.cents * self._percent_off) // 100
        return Money(base_total.cents - discount_cents)
    return base_total
```
<!-- slide -->
```python
# Task 9: playground/events.py -> EventBus.__contains__
def __contains__(self, event_type: object) -> bool:
    """Return whether any handlers are registered for event_type."""
    if not isinstance(event_type, EventType):
        return False
    return event_type in self._subscribers and len(self._subscribers[event_type]) > 0
```
<!-- slide -->
```python
# Task 10: playground/models.py -> Money.__bool__
def __bool__(self) -> bool:
    """Return True when the amount is non-zero."""
    return self._cents != 0
```
````

---

## 5. Execution & Verification Instructions

To re-run the pipeline or execute the test suite independently:

```bash
# Run full RAG pipeline across all tasks and execute unit tests:
uv run rag_pipeline.py

# Run only the test suite:
uv run rag_pipeline.py --run-tests-only

# Run pipeline with another authorized model (e.g. gpt-5.6-luna):
uv run rag_pipeline.py --model gpt-5.6-luna
```
