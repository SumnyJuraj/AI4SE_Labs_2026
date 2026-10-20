import streamlit as st
import json
import os
from pathlib import Path
from pyvis.network import Network
import streamlit.components.v1 as components

from src.graph import create_requirements_graph
from src.state import GraphState

st.set_page_config(
    page_title="Requirements Refinement & Traceability Visualizer",
    page_icon="🕸️",
    layout="wide"
)

st.title("🕸️ Requirements Refinement & Traceability Visualizer")
st.caption("Agentic LangGraph Network for Automated Requirements Consolidation (Evergreen ILS)")

# --- Sidebar ---
st.sidebar.header("⚙️ Konfigurácia")
corpus_dir = st.sidebar.text_input("Vstupný priečinok korpusu", value="data/corpus")
output_file = st.sidebar.text_input("Výstupný SRS súbor", value="requirements.md")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Aktívne AI modely v sieti")
st.sidebar.info(
    "• **Node 1: Ingestor**: Deterministický Python (ANS2)\n"
    "• **Node 2: Extractor**: `gpt-4o-mini` (LLM 1 – ANS1, ANS4)\n"
    "• **Node 3: Consolidator**: `gpt-5.6-luna` (LLM 2 – ANS1, ANS4)\n"
    "• **Node 4: Quality Critic**: `gpt-6-luna` (LLM 3 – ANS1, ANS3 Feedback, ANS4)\n"
    "• **Node 5: Builder**: Deterministický Python (ANS2)"
)

run_pipeline = st.sidebar.button("🚀 Spustiť novú LangGraph pipeline", type="primary")

# --- Helper Functions ---
def load_existing_artifacts():
    req_file = Path("requirements.md")
    graph_file = Path("requirements_graph.json")
    if req_file.exists() and graph_file.exists():
        with open(graph_file, "r", encoding="utf-8") as f:
            graph_data = json.load(f)
        with open(req_file, "r", encoding="utf-8") as f:
            doc_content = f.read()
        return graph_data, doc_content
    return None, None

def get_agent_nodes_definition():
    """Returns specialized nodes and metadata representing each agent in the LangGraph network."""
    return [
        {
            "id": "AGENT:INGESTION",
            "label": "📥 Node 1: Ingestor\n(Python)",
            "group": "Agent",
            "title": "<b>Node 1: Ingestor & Preprocessing</b><br>Type: Deterministic (ANS2)<br>Role: Crawls input directory, parses .eml/.txt files",
            "shape": "hexagon",
            "size": 28,
            "color": "#8b5cf6",
            "full_data": {
                "id": "AGENT:INGESTION",
                "title": "Node 1: Ingestor & Document Parser",
                "category": "Deterministic Component (ANS2)",
                "priority": "System Node",
                "description": "Scans the input directory recursively, parses RFC-compliant .eml headers (From, To, Subject, Date) and plain text .txt files. Feeds normalized document items into the extraction pipeline.",
                "model": "Pure Python (RFC email parser)",
                "role": "Deterministic data ingestion",
                "specs": "ANS2 (Deterministic Node), OS4 (Initial document provenance)",
                "source_documents": ["data/corpus (20 súborov)"]
            }
        },
        {
            "id": "AGENT:EXTRACTOR",
            "label": "⚡ Node 2: Extractor\n(gpt-4o-mini)",
            "group": "Agent",
            "title": "<b>Node 2: Requirement Extractor</b><br>Model: gpt-4o-mini (ANS1, ANS4)<br>Role: Extracts atomic candidate requirements from each document",
            "shape": "hexagon",
            "size": 32,
            "color": "#9333ea",
            "full_data": {
                "id": "AGENT:EXTRACTOR",
                "title": "Node 2: Requirement Extractor Node",
                "category": "Agentic LLM Node (ANS1, ANS4)",
                "priority": "System Node",
                "description": "Executes concurrent LLM extraction across all corpus documents using a ThreadPoolExecutor. Identifies every functional capability, rule, constraint, and user need. Yielded 252 raw candidate requirements.",
                "model": "gpt-4o-mini",
                "role": "High-throughput candidate extraction",
                "specs": "ANS1 (Agentic Node), ANS4 (Model 1), OS4 (Document tracing), OS8 (Completeness)",
                "source_documents": ["Všetky vstupné dokumenty korpusu"]
            }
        },
        {
            "id": "AGENT:CONSOLIDATOR",
            "label": "🧠 Node 3: Consolidator\n(gpt-5.6-luna)",
            "group": "Agent",
            "title": "<b>Node 3: Consolidator & Deduplicator</b><br>Model: gpt-5.6-luna (ANS1, ANS4)<br>Role: Merges duplicates, categorizes, assigns MoSCoW, creates Blacklist",
            "shape": "hexagon",
            "size": 34,
            "color": "#7c3aed",
            "full_data": {
                "id": "AGENT:CONSOLIDATOR",
                "title": "Node 3: Consolidator & Deduplicator Node",
                "category": "Agentic LLM Node (ANS1, ANS4)",
                "priority": "System Node",
                "description": "Performs deep semantic synthesis across all 252 raw extractions. Removes redundancies, unifies Evergreen terminology, assigns IDs (REQ-CAT-001, etc.), assigns MoSCoW priorities, and moves invalid proposals to Blacklist. Capable of receiving feedback from Critic.",
                "model": "gpt-5.6-luna",
                "role": "Semantic consolidation, prioritization & conflict resolution",
                "specs": "ANS1 (Agentic Node), ANS4 (Model 2), OS2 (IDs), OS3 (No duplicates), OS5 (Descriptions), OS6 (MoSCoW), OS7 (Consistency), OS9 (Blacklist)",
                "source_documents": ["252 surových požiadaviek z Node 2"]
            }
        },
        {
            "id": "AGENT:CRITIC",
            "label": "🕵️ Node 4: Critic & Auditor\n(gpt-6-luna)",
            "group": "Agent",
            "title": "<b>Node 4: Quality Critic & Auditor</b><br>Model: gpt-6-luna (ANS1, ANS3, ANS4)<br>Role: Autonomous audit against OS1-OS9, triggers Feedback Loop",
            "shape": "hexagon",
            "size": 32,
            "color": "#6d28d9",
            "full_data": {
                "id": "AGENT:CRITIC",
                "title": "Node 4: Quality Critic & Auditor Node",
                "category": "Agentic LLM Node & Feedback Trigger (ANS1, ANS3, ANS4)",
                "priority": "System Node",
                "description": "Rigorous reasoning auditor using gpt-6-luna. Evaluates requirements against OS1-OS9 specifications. In Iteration 1, found 2 issues and rejected approval (Score 91/100), triggering the feedback loop back to Node 3. In Iteration 2, approved the revised set with Score 94/100.",
                "model": "gpt-6-luna",
                "role": "Autonomous auditing & Feedback loop control",
                "specs": "ANS1 (Agentic Node), ANS3 (Feedback Loop), ANS4 (Model 3), Quality governance",
                "source_documents": ["Výstupy z Node 3 (Consolidator)"]
            }
        },
        {
            "id": "AGENT:BUILDER",
            "label": "📋 Node 5: Builder\n(Python)",
            "group": "Agent",
            "title": "<b>Node 5: Document & Graph Builder</b><br>Type: Deterministic (ANS2)<br>Role: Compiles requirements.md and requirements_graph.json",
            "shape": "hexagon",
            "size": 28,
            "color": "#8b5cf6",
            "full_data": {
                "id": "AGENT:BUILDER",
                "title": "Node 5: Document & Graph Builder Node",
                "category": "Deterministic Component (ANS2)",
                "priority": "System Node",
                "description": "Deterministic Python node assembling the verified state into a 515-line Software Requirements Specification (requirements.md) including priority scale explanation, master table, detailed catalog, blacklist, and audit log.",
                "model": "Pure Python (Markdown / JSON serializer)",
                "role": "Artifact generation & graph export",
                "specs": "ANS2 (Deterministic Node), OS1 (Single document), OS6 (Priority scale explanation)",
                "source_documents": ["Validovaný stav celej siete"]
            }
        }
    ]

def render_pyvis_network(nodes, edges, layout_type="physics", height="620px"):
    net = Network(height=height, width="100%", bgcolor="#ffffff", font_color="#0f172a", directed=True)
    
    if layout_type == "hierarchical":
        net.set_options("""
        var options = {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "direction": "LR",
              "sortMethod": "directed",
              "levelSeparation": 280,
              "nodeSpacing": 100,
              "treeSpacing": 140
            }
          },
          "physics": {
            "hierarchicalRepulsion": {
              "centralGravity": 0.0,
              "springLength": 180,
              "springConstant": 0.01,
              "nodeDistance": 160,
              "damping": 0.09
            },
            "solver": "hierarchicalRepulsion"
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "tooltipDelay": 150
          }
        }
        """)
    else:
        # Physics / Force-directed layout
        net.set_options("""
        var options = {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -120,
              "centralGravity": 0.01,
              "springLength": 200,
              "springStrength": 0.05,
              "damping": 0.5
            },
            "maxVelocity": 40,
            "minVelocity": 0.1,
            "solver": "forceAtlas2Based",
            "stabilization": { "iterations": 180 }
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "tooltipDelay": 150
          }
        }
        """)
    
    for n in nodes:
        net.add_node(
            n["id"],
            label=n["label"],
            title=n.get("title", ""),
            color=n.get("color", "#95a5a6"),
            shape=n.get("shape", "dot"),
            size=n.get("size", 18),
            borderWidth=2
        )
        
    for e in edges:
        net.add_edge(
            e["from"],
            e["to"],
            title=e.get("title", ""),
            color=e.get("color", "#94a3b8"),
            dashes=e.get("dashes", False),
            arrows="to"
        )
        
    tmp_path = Path(".streamlit_cache_graph.html")
    net.save_graph(str(tmp_path))
    with open(tmp_path, "r", encoding="utf-8") as f:
        html_code = f.read()
    return html_code

# --- Execution Logic ---
if run_pipeline:
    st.info("🔄 Spúšťam LangGraph pipeline... Sleduj logy v termináli.")
    app = create_requirements_graph()
    initial_state: GraphState = {
        "input_dir": corpus_dir,
        "documents": [],
        "raw_requirements": [],
        "consolidated_requirements": [],
        "blacklisted_requirements": [],
        "audit_feedback": None,
        "iteration": 0,
        "final_document": "",
        "graph_data": {},
        "logs": []
    }
    with st.spinner("Agenti čítajú korpus, extrahujú požiadavky, konsolidujú a vykonávajú audit..."):
        result = app.invoke(initial_state)
        st.session_state["graph_data"] = result["graph_data"]
        st.session_state["final_document"] = result["final_document"]
        st.session_state["logs"] = result["logs"]
        st.session_state["requirements"] = result["consolidated_requirements"]
        st.session_state["blacklisted"] = result["blacklisted_requirements"]
        st.session_state["feedback"] = result["audit_feedback"]
    st.success("✅ LangGraph pipeline úspešne dokončená!")

# Ensure state is populated from existing files if not already in session
if "graph_data" not in st.session_state:
    g_data, d_content = load_existing_artifacts()
    if g_data:
        st.session_state["graph_data"] = g_data
        st.session_state["final_document"] = d_content

# --- High-Contrast Visual Color Legend (6 Cards) ---
st.markdown("### 🎨 Vizuálna legenda prvkov v grafe")
st.markdown(
    """
    <style>
    .legend-card {
        padding: 8px 12px;
        border-radius: 8px;
        color: #0f172a !important;
        font-family: sans-serif;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        margin-bottom: 8px;
    }
    .legend-title {
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 2px;
        color: #0f172a !important;
    }
    .legend-desc {
        font-size: 11px;
        color: #334155 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(
        """
        <div class="legend-card" style="background-color: #ede9fe; border: 2px solid #7c3aed;">
            <div class="legend-title">🟪 AI Agent / Uzol</div>
            <div class="legend-desc">LLM uzol / Python (ANS1-5)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="legend-card" style="background-color: #bae6fd; border: 2px solid #0284c7;">
            <div class="legend-title">🟦 Zdrojový súbor</div>
            <div class="legend-desc">Vstupný dokument (.txt, .eml)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div class="legend-card" style="background-color: #fecaca; border: 2px solid #dc2626;">
            <div class="legend-title">🟥 Must Have (P1)</div>
            <div class="legend-desc">Kritická požiadavka</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        """
        <div class="legend-card" style="background-color: #fef08a; border: 2px solid #ca8a04;">
            <div class="legend-title">🟧 Should Have (P2)</div>
            <div class="legend-desc">Dôležitá funkcia</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c5:
    st.markdown(
        """
        <div class="legend-card" style="background-color: #bbf7d0; border: 2px solid #16a34a;">
            <div class="legend-title">🟩 Could Have (P3)</div>
            <div class="legend-desc">Rozšírenie / doplnok</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c6:
    st.markdown(
        """
        <div class="legend-card" style="background-color: #e2e8f0; border: 2px solid #475569;">
            <div class="legend-title">⬛ Blacklist (OS9)</div>
            <div class="legend-desc">Vyradený návrh</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("")

# --- Main Tabs ---
tabs = st.tabs([
    "🕸️ Traceability Graf & Agenti",
    "📋 Katalóg požiadaviek (Tabuľka)",
    "🚫 Blacklist (Vyradené položky)",
    "📄 Finálny SRS Dokument",
    "📊 Záznam auditu & Feedback Loop"
])

graph_data = st.session_state.get("graph_data")
doc_text = st.session_state.get("final_document", "")

if not graph_data:
    st.warning("⚠️ Zatiaľ nie sú vygenerované žiadne požiadavky. Klikni vľavo na tlačidlo **'🚀 Spustiť novú LangGraph pipeline'**.")
else:
    all_nodes = graph_data["nodes"]
    all_edges = graph_data["edges"]
    req_nodes = [n for n in all_nodes if n["id"].startswith("REQ:")]
    doc_nodes = [n for n in all_nodes if n["id"].startswith("DOC:")]
    blk_nodes = [n for n in all_nodes if n["id"].startswith("BLK:")]
    agent_nodes = get_agent_nodes_definition()

    # --- TAB 1: Traceability Graph & Agents ---
    with tabs[0]:
        st.markdown(
            """
            > 💡 **Ako sa tu orientovať:**  
            > - **Zobrazenie agentov:** Prepínač nižšie ti umožňuje zobraziť **vlastný uzol pre každého jedného agenta** (`gpt-4o-mini`, `gpt-5.6-luna`, `gpt-6-luna`), takže presne vidíš, cez koho dáta tečú!  
            > - **Feedback Loop:** Medzi *Consolidatorom* a *Criticom* vidíš obojsmerné prepojenie – v 1. iterácii Critic návrh zamietol a vrátil ho Consolidatorovi na prepracovanie.  
            > - **Hierarchický režim:** Prepni layout na *Zľava doprava (Hierarchický)* – vľavo uvidíš dokumenty, v strede agentov a vpravo vygenerované požiadavky.
            """
        )

        fc1, fc2, fc3 = st.columns([3, 2, 2])
        
        with fc1:
            view_mode = st.radio(
                "🔀 Typ prepojení v grafe:",
                [
                    "🤖 Tok cez agentov (Súbory ➔ Agenti ➔ Požiadavky)",
                    "🔗 Priame trasovanie (Súbory ➔ Požiadavky)",
                    "🏛️ Iba sieť agentov (Čistá LangGraph architektúra)"
                ],
                index=0
            )

        with fc2:
            categories = sorted(list(set(n.get("full_data", {}).get("category", "General") for n in req_nodes)))
            selected_cat = st.selectbox("🎯 Filter podľa kategórie (podsystému):", ["Všetky kategórie (Celý graf)"] + categories)

        with fc3:
            layout_choice = st.radio(
                "📐 Režim usporiadania grafu:",
                ["Zľava doprava (Hierarchický - prehľadný)", "Fyzikálny klastrový (Voľný pohyb)"],
                index=0
            )
            layout_type = "hierarchical" if "Hierarchický" in layout_choice else "physics"

        # Filter active requirements by category
        filtered_req_nodes = req_nodes
        if selected_cat != "Všetky kategórie (Celý graf)":
            filtered_req_nodes = [n for n in req_nodes if n.get("full_data", {}).get("category") == selected_cat]

        active_req_ids = set(n["id"] for n in filtered_req_nodes)

        # Assemble nodes & edges based on view_mode
        display_nodes = []
        display_edges = []

        if view_mode == "🏛️ Iba sieť agentov (Čistá LangGraph architektúra)":
            display_nodes = agent_nodes
            display_edges = [
                {"from": "AGENT:INGESTION", "to": "AGENT:EXTRACTOR", "title": "20 načítaných dokumentov"},
                {"from": "AGENT:EXTRACTOR", "to": "AGENT:CONSOLIDATOR", "title": "252 vyťažených surových požiadaviek"},
                {"from": "AGENT:CONSOLIDATOR", "to": "AGENT:CRITIC", "title": "Odoslanie návrhu SRS na audit kvality"},
                {"from": "AGENT:CRITIC", "to": "AGENT:CONSOLIDATOR", "title": "Feedback loop: Odmietnutie v 1. iterácii (Score 91/100, 2 issues) -> prepracovanie", "dashes": True, "color": "#ef4444"},
                {"from": "AGENT:CRITIC", "to": "AGENT:BUILDER", "title": "Audit schválený v 2. iterácii (Score 94/100, Approved)"},
                {"from": "AGENT:BUILDER", "to": "AGENT:BUILDER", "title": "Finálny requirements.md"}
            ]

        elif view_mode == "🤖 Tok cez agentov (Súbory ➔ Agenti ➔ Požiadavky)":
            # Files -> Ingestor -> Extractor -> Consolidator <-> Critic -> Builder -> Reqs / Blacklist
            display_nodes.extend(agent_nodes)
            display_nodes.extend(doc_nodes)
            display_nodes.extend(filtered_req_nodes)
            if selected_cat == "Všetky kategórie (Celý graf)":
                display_nodes.extend(blk_nodes)

            # 1. Docs to Ingestor
            for d in doc_nodes:
                display_edges.append({
                    "from": d["id"],
                    "to": "AGENT:INGESTION",
                    "title": f"Načítanie: {d['label']}",
                    "color": "#94a3b8"
                })

            # 2. Pipeline flow
            display_edges.append({"from": "AGENT:INGESTION", "to": "AGENT:EXTRACTOR", "title": "20 dokumentov", "color": "#8b5cf6"})
            display_edges.append({"from": "AGENT:EXTRACTOR", "to": "AGENT:CONSOLIDATOR", "title": "252 raw požiadaviek", "color": "#9333ea"})
            
            # Feedback Loop between Consolidator and Critic
            display_edges.append({"from": "AGENT:CONSOLIDATOR", "to": "AGENT:CRITIC", "title": "Návrh na audit kvality", "color": "#7c3aed"})
            display_edges.append({
                "from": "AGENT:CRITIC",
                "to": "AGENT:CONSOLIDATOR",
                "title": "Feedback Loop (ANS3): Critic našiel 2 issues v 1. iterácii -> vrátené na opravu",
                "dashes": True,
                "color": "#dc2626"
            })
            display_edges.append({"from": "AGENT:CRITIC", "to": "AGENT:BUILDER", "title": "Schválenie auditu (Score 94/100)", "color": "#16a34a"})

            # 3. Builder to Requirements & Blacklist
            for r in filtered_req_nodes:
                display_edges.append({
                    "from": "AGENT:BUILDER",
                    "to": r["id"],
                    "title": f"Výstup: {r['id']}",
                    "color": r.get("color", "#cbd5e1")
                })
                
            if selected_cat == "Všetky kategórie (Celý graf)":
                for b in blk_nodes:
                    display_edges.append({
                        "from": "AGENT:BUILDER",
                        "to": b["id"],
                        "title": f"Vyradené: {b['id']}",
                        "dashes": True,
                        "color": "#94a3b8"
                    })

        else: # Priame trasovanie (Súbory -> Požiadavky)
            needed_doc_ids = set()
            for e in all_edges:
                if e["to"] in active_req_ids:
                    display_edges.append(e)
                    needed_doc_ids.add(e["from"])

            filtered_doc_nodes = [n for n in doc_nodes if n["id"] in needed_doc_ids]
            display_nodes = filtered_doc_nodes + filtered_req_nodes
            if selected_cat == "Všetky kategórie (Celý graf)":
                display_nodes.extend(blk_nodes)
                for b in blk_nodes:
                    for e in all_edges:
                        if e["to"] == b["id"]:
                            display_edges.append(e)

        st.caption(f"Aktuálny náhľad: **{len(display_nodes)}** uzlov a **{len(display_edges)}** prepojení.")
        
        html_network = render_pyvis_network(display_nodes, display_edges, layout_type=layout_type, height="620px")
        components.html(html_network, height=640)

        # Unified Inspector Box (for both Requirements AND Agents!)
        st.markdown("---")
        st.subheader("🔍 Inšpektor uzla (Klikni a prečítaj detail)")
        
        inspect_options = [n["id"] for n in display_nodes]
        selected_node_id = st.selectbox(
            "Vyber uzol (AI agenta, požiadavku alebo súbor) pre zobrazenie podrobností:",
            options=inspect_options,
            format_func=lambda x: next(n["label"].replace("\n", " ") for n in display_nodes if n["id"] == x)
        )
        
        node_match = next((n for n in display_nodes if n["id"] == selected_node_id), None)
        if node_match:
            r_data = node_match.get("full_data", {})
            icol1, icol2 = st.columns([3, 2])
            with icol1:
                st.markdown(f"### `{r_data.get('id', node_match['id'])}`: {r_data.get('title', node_match['label'])}")
                if r_data.get("model"):
                    st.success(f"🤖 **Použitý AI Model / Typ:** `{r_data.get('model')}`")
                if r_data.get("specs"):
                    st.info(f"📌 **Splnené špecifikácie zadania:** `{r_data.get('specs')}`")
                st.markdown(f"**Priorita / Skupina:** `{r_data.get('priority', node_match.get('group'))}` | **Kategória:** `{r_data.get('category', 'N/A')}`")
                if r_data.get("rationale"):
                    st.info(f"**Architektonické odôvodnenie:** {r_data.get('rationale')}")
                st.markdown("**Popis a správanie:**")
                st.write(r_data.get("description", "Bez popisu."))
            with icol2:
                if node_match["id"].startswith("AGENT:"):
                    st.markdown("#### ⚙️ Úloha agenta v sieti:")
                    st.code(f"Úloha: {r_data.get('role', 'N/A')}\nVstup: {', '.join(r_data.get('source_documents', []))}", language="text")
                else:
                    st.markdown("#### 📄 Zdrojové dokumenty (Traceability):")
                    for s in r_data.get("source_documents", []):
                        st.code(f"📄 {s}", language="text")

    # --- TAB 2: Master Requirements Catalog ---
    with tabs[1]:
        st.subheader("📋 Prehľadná tabuľka všetkých konsolidovaných požiadaviek")
        st.write("Tu vidíš všetky vygenerované požiadavky v štruktúrovanej tabuľke, pripravené na vyhľadávanie a filtrovanie.")
        
        catalog_rows = []
        for n in req_nodes:
            d = n.get("full_data", {})
            catalog_rows.append({
                "ID": d.get("id"),
                "Názov požiadavky": d.get("title"),
                "Priorita (MoSCoW)": d.get("priority"),
                "Kategória / Subsystém": d.get("category"),
                "Počet zdrojov": len(d.get("source_documents", [])),
                "Zdrojové dokumenty": ", ".join(d.get("source_documents", []))
            })
            
        p_filter = st.multiselect(
            "Filtrovať podľa priority:",
            options=["Must Have", "Should Have", "Could Have", "Won't Have"],
            default=["Must Have", "Should Have"]
        )
        filtered_table = [r for r in catalog_rows if r["Priorita (MoSCoW)"] in p_filter]
        st.dataframe(filtered_table, use_container_width=True)

    # --- TAB 3: Blacklist ---
    with tabs[2]:
        st.subheader("🚫 Blacklist – Vyradené a neplatné požiadavky (OS9)")
        st.write(
            "Zadanie vyžaduje zaznamenať v osobitnej sekcii požiadavky, ktoré boli vyradené "
            "(napr. administratívne úkony, neplatné predstavy, nekonzistentné návrhy) spolu s vysvetlením dôvodu."
        )
        if not blk_nodes:
            st.info("Žiadne požiadavky neboli vyradené.")
        else:
            for b_node in blk_nodes:
                b = b_node.get("full_data", {})
                with st.expander(f"🚫 [{b.get('id')}] {b.get('title')}", expanded=True):
                    st.markdown(f"**Dôvod vyradenia:** :red[{b.get('reason_for_discarding')}]")
                    st.markdown(f"**Pôvodný návrh z textu:** {b.get('description')}")
                    st.markdown(f"**Kde sa objavil (zdroje):** `{', '.join(b.get('source_documents', []))}`")

    # --- TAB 4: Final SRS Document ---
    with tabs[3]:
        st.subheader("📄 Finálny štruktúrovaný dokument požiadaviek (SRS)")
        st.download_button(
            "📥 Stiahnuť vygenerovaný requirements.md",
            data=doc_text,
            file_name="requirements.md",
            mime="text/markdown"
        )
        st.markdown(doc_text)

    # --- TAB 5: Pipeline Logs & Audit ---
    with tabs[4]:
        st.subheader("📊 Záznam z auditu kvality a priebehu siete")
        st.markdown(
            """
            Tu je zaznamenané, ako prebiehal **Feedback Loop (ANS3)** medzi uzlami:
            1. **Extractor** (`gpt-4o-mini`) vyťažil 252 kandidátov.
            2. **Consolidator** (`gpt-5.6-luna`) vytvoril prvý návrh.
            3. **Critic** (`gpt-6-luna`) našiel 2 nejasnosti, neschválil dokument (`Approved=False`, 91/100) a poslal ho späť do Consolidatora.
            4. **Consolidator** (Iterácia 2) opravil pripomienky.
            5. **Critic** schválil revidovanú verziu (`Approved=True`, **94/100**).
            """
        )
        logs = st.session_state.get("logs", [])
        if logs:
            for l in logs:
                st.code(l, language="text")
        else:
            st.write("Dáta boli načítané z disku. Pri novom spustení sa tu zobrazia živé systémové logy.")
