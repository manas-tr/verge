import base64
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="Verge",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


API_URL = "https://verge-api.onrender.com/"
RECOMMEND_ENDPOINT = f"{API_URL.rstrip('/')}/recommend"
ROOT_DIR = Path(__file__).resolve().parent
VISUAL_PATH = ROOT_DIR / "reduce_co2.jpg"


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def format_energy(val: float) -> str:
    return f"{val:,.0f} J"


def format_seconds(val: float) -> str:
    if float(val).is_integer():
        return f"{int(val):,} sec"
    return f"{val:,.1f} sec"


def to_dataframe(items: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(items)
    if not df.empty:
        cols = [c for c in ["cpus", "mem", "pred_energy", "score"] if c in df.columns]
        df = df[cols]
    return df


def find_requested_config(items: List[Dict[str, Any]], cpus: int, mem: int) -> Dict[str, Any]:
    for item in items:
        if item.get("cpus") == cpus and item.get("mem") == mem:
            return item
    return {}


@st.cache_data(ttl=10, show_spinner=False)
def api_status() -> Dict[str, Any]:
    start = perf_counter()
    try:
        response = requests.get(API_URL, timeout=1.5)
        latency_ms = round((perf_counter() - start) * 1000)
        return {"online": response.ok, "latency_ms": latency_ms}
    except requests.RequestException:
        return {"online": False, "latency_ms": None}


@st.cache_data(show_spinner=False)
def call_api(payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(RECOMMEND_ENDPOINT, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


co2_image_uri = image_data_uri(VISUAL_PATH)
status = api_status()
status_text = f"API online {status['latency_ms']} ms" if status["online"] else "API offline"
status_class = "api-ok" if status["online"] else "api-down"


st.markdown(
    """
    <style>
        :root {
            --ink: #17201b;
            --muted: #66716b;
            --line: #e7ebe8;
            --soft: #f5f8f6;
            --green: #23864d;
            --green-dark: #17643a;
            --green-light: #eaf5ee;
            --white: #ffffff;
        }

        * {
            box-sizing: border-box;
            letter-spacing: 0;
        }

        .stApp {
            background: var(--white);
            color: var(--ink);
        }

        header[data-testid="stHeader"] {
            background: transparent;
            height: 0;
        }

        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"] {
            display: none;
        }

        .block-container {
            max-width: 1180px;
            padding: 1.25rem 2rem 2.5rem;
        }

        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.85rem 0 1.25rem;
            border-bottom: 1px solid var(--line);
        }

        .brand {
            color: var(--green);
            font-size: 1.2rem;
            font-weight: 800;
        }

        .nav {
            display: flex;
            align-items: center;
            gap: 1.25rem;
            color: var(--muted);
            font-size: 0.92rem;
        }

        .api-pill {
            border: 1px solid var(--line);
            border-radius: 999px;
            padding: 0.28rem 0.68rem;
            font-family: Consolas, "Courier New", monospace;
            font-size: 0.78rem;
            line-height: 1.2;
            white-space: nowrap;
        }

        .api-ok {
            color: var(--green-dark);
            background: var(--green-light);
        }

        .api-down {
            color: #8a1f1f;
            background: #fbefef;
        }

        .nav a,
        .run-actions a {
            color: var(--muted);
            text-decoration: none;
        }

        .nav a:hover,
        .run-actions a:hover {
            color: var(--green);
        }

        .intro {
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(300px, 420px);
            gap: 3rem;
            align-items: center;
            padding: 3.5rem 0 2.75rem;
        }

        .run-kicker {
            color: var(--muted);
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 0.7rem;
        }

        .run-title {
            margin: 0;
            color: var(--ink);
            font-size: clamp(2.55rem, 5vw, 4.35rem);
            font-weight: 850;
            line-height: 1.02;
        }

        .run-title span {
            color: var(--green);
        }

        .run-copy {
            max-width: 560px;
            color: var(--muted);
            font-size: 1.03rem;
            line-height: 1.7;
            margin: 1.35rem 0 1.7rem;
        }

        .run-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            align-items: center;
        }

        .primary-link,
        .secondary-link {
            display: inline-flex;
            align-items: center;
            min-height: 42px;
            padding: 0.72rem 1.05rem;
            border-radius: 6px;
            font-weight: 750;
            font-size: 0.95rem;
        }

        .primary-link {
            background: var(--green);
            color: var(--white) !important;
        }

        .primary-link:hover {
            background: var(--green-dark);
            color: var(--white) !important;
        }

        .secondary-link {
            border: 1px solid var(--line);
            color: var(--ink) !important;
        }

        .co2-panel {
            min-height: 380px;
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            background: var(--soft);
        }

        .co2-panel img {
            width: 100%;
            height: 100%;
            min-height: 380px;
            object-fit: cover;
            object-position: 70% 58%;
            display: block;
            filter: saturate(0.9);
        }

        .co2-panel-fallback {
            height: 380px;
            display: grid;
            align-content: center;
            gap: 1rem;
            padding: 2rem;
        }

        .co2-line {
            height: 12px;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--green), #9ac87f);
        }

        .section-title {
            color: var(--ink);
            font-size: 1.55rem;
            font-weight: 800;
            margin: 0 0 0.35rem;
        }

        .section-note {
            color: var(--muted);
            margin: 0 0 1.25rem;
            font-size: 0.95rem;
        }

        .section-space {
            padding-top: 1.15rem;
            border-top: 1px solid var(--line);
            margin-top: 1rem;
        }

        .stButton > button {
            background: var(--green) !important;
            color: white !important;
            border: 0 !important;
            border-radius: 6px !important;
            padding: 0.72rem 1.25rem !important;
            font-weight: 750 !important;
            min-height: 42px !important;
        }

        .stButton > button:hover {
            background: var(--green-dark) !important;
            color: white !important;
            border: 0 !important;
        }

        div[data-testid="stForm"] {
            border: 1px solid var(--line);
            background: var(--soft);
            border-radius: 8px;
            padding: 1.25rem 1.25rem 1rem;
        }

        .notice {
            background: var(--green-light);
            border-left: 4px solid var(--green);
            color: var(--ink);
            padding: 1rem 1.1rem;
            border-radius: 6px;
            margin: 1rem 0;
            line-height: 1.55;
        }

        .run-strip {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            margin: 1rem 0 0.9rem;
            color: var(--muted);
            font-family: Consolas, "Courier New", monospace;
            font-size: 0.9rem;
            overflow-wrap: anywhere;
        }

        .delta-line {
            margin-top: 0.45rem;
            color: var(--ink);
        }

        .metric {
            background: white;
            border: 1px solid var(--line);
            border-left: 4px solid var(--green);
            border-radius: 8px;
            padding: 1.05rem 1rem;
            min-height: 112px;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 750;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .metric-value {
            color: var(--green);
            font-size: 1.45rem;
            font-weight: 850;
            overflow-wrap: anywhere;
        }

        .flow-line {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.9rem 1rem;
            margin-top: 0.8rem;
            color: var(--muted);
            font-family: Consolas, "Courier New", monospace;
            font-size: 0.92rem;
        }

        @media (max-width: 780px) {
            .block-container {
                padding: 1rem 1.1rem 2rem;
            }

            .topbar,
            .nav,
            .run-actions {
                align-items: flex-start;
                flex-direction: column;
            }

            .intro {
                grid-template-columns: 1fr;
            }

            .intro {
                gap: 1.6rem;
                padding: 2.25rem 0 1.75rem;
            }

            .co2-panel,
            .co2-panel img,
            .co2-panel-fallback {
                min-height: 260px;
                height: 260px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.sidebar.markdown("## Verge")
st.sidebar.markdown("Workload energy estimator.")
st.sidebar.markdown("### Endpoint")
st.sidebar.code(RECOMMEND_ENDPOINT, language="text")


st.markdown(
    f"""
    <div class="topbar">
        <div class="brand">Verge</div>
        <div class="nav">
            <a href="#job-planner">Job spec</a>
            <a href="#results">Rankings</a>
            <span>Select</span>
            <span class="api-pill {status_class}">{status_text}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


if co2_image_uri:
    co2_panel_markup = f'<div class="co2-panel"><img src="{co2_image_uri}" alt="CO2 reduction mark"></div>'
else:
    co2_panel_markup = """
    <div class="co2-panel co2-panel-fallback">
        <div class="co2-line" style="width: 92%;"></div>
        <div class="co2-line" style="width: 72%;"></div>
        <div class="co2-line" style="width: 54%;"></div>
    </div>
    """


st.markdown(
    f"""
    <section class="intro">
        <div>
            <div class="run-kicker">Scheduler input. Energy output.</div>
            <h1 class="run-title">Find the <span>lowest-energy</span><br>run config.</h1>
            <p class="run-copy">
                Send the job spec. Verge scores CPU and memory choices, then returns the config with the lowest estimated energy use.
            </p>
            <div class="run-actions">
                <a class="primary-link" href="#job-planner">Edit job spec</a>
                <a class="secondary-link" href="#results">View rankings</a>
            </div>
        </div>
        {co2_panel_markup}
    </section>
    """,
    unsafe_allow_html=True,
)


st.markdown('<span id="job-planner"></span>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-space">
        <h2 class="section-title">Job spec</h2>
        <p class="section-note">Use the same numbers you would hand to the scheduler.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.form("job_form", clear_on_submit=False):
    c1, c2 = st.columns(2)
    with c1:
        cpus_req = st.number_input("CPUs requested", min_value=1, value=8, step=1)
        nodes_alloc = st.number_input("Nodes allocated", min_value=1, value=1, step=1)
        timelimit = st.number_input("Time limit (sec)", min_value=1, value=3600, step=60)
        avgmemoryutilization_pct = st.number_input("Avg memory util (%)", min_value=0.0, value=50.0, step=1.0)
    with c2:
        mem_req = st.number_input("Memory requested (MB)", min_value=1, value=32000, step=1000)
        priority = st.number_input("Priority", min_value=0, value=100, step=1)
        job_duration_sec = st.number_input("Job duration (sec)", min_value=1.0, value=2000.0, step=100.0)
        avgsmutilization_pct = st.number_input("Avg SM util (%)", min_value=0.0, value=60.0, step=1.0)

    submitted = st.form_submit_button("Score configs")


st.markdown('<span id="results"></span>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-space">
        <h2 class="section-title">Rankings</h2>
    </div>
    """,
    unsafe_allow_html=True,
)


if submitted:
    payload = {
        "cpus_req": int(cpus_req),
        "mem_req": int(mem_req),
        "nodes_alloc": int(nodes_alloc),
        "priority": int(priority),
        "timelimit": int(timelimit),
        "job_duration_sec": float(job_duration_sec),
        "avgmemoryutilization_pct": float(avgmemoryutilization_pct),
        "avgsmutilization_pct": float(avgsmutilization_pct),
    }

    try:
        start = perf_counter()
        with st.spinner("Scoring configs..."):
            data = call_api(payload)
        request_ms = round((perf_counter() - start) * 1000)

        selected = data.get("best_config", {})
        recs = data.get("recommendations", [])
        pod = data.get("pod", "-")

        selected_energy = selected.get("pred_energy", 0.0)
        selected_cpus = selected.get("cpus", cpus_req)
        selected_mem = selected.get("mem", mem_req)
        requested = find_requested_config(recs, int(cpus_req), int(mem_req))
        requested_energy = requested.get("pred_energy")
        delta_text = "Energy delta vs requested: n/a"
        if requested_energy:
            delta_pct = ((selected_energy - requested_energy) / requested_energy) * 100
            delta_text = f"Energy delta vs requested: {delta_pct:+.1f}%"

        st.markdown(
            f"""
            <div class="run-strip">
                request: {int(cpus_req)} CPU | {int(mem_req):,} MB | nodes {int(nodes_alloc)} |
                limit {format_seconds(float(timelimit))} | runtime {format_seconds(float(job_duration_sec))} |
                mem util {float(avgmemoryutilization_pct):.0f}% | sm util {float(avgsmutilization_pct):.0f}% |
                POST /recommend | {request_ms} ms
                <div class="delta-line">{delta_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="notice">
                <strong>Selected config:</strong> {selected_cpus} CPUs with {selected_mem:,} MB memory<br>
                <strong>Estimated energy:</strong> {format_energy(selected_energy)} | <strong>Pod:</strong> {pod}
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""
                <div class="metric">
                    <div class="metric-label">CPU</div>
                    <div class="metric-value">{selected_cpus}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div class="metric">
                    <div class="metric-label">Memory</div>
                    <div class="metric-value">{selected_mem:,} MB</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""
                <div class="metric">
                    <div class="metric-label">Energy estimate</div>
                    <div class="metric-value">{format_energy(selected_energy)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("### Candidate configs")
        df = to_dataframe(recs)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Could not evaluate: {e}")
else:
    st.markdown(
        """
        <div class="notice">
            Score a job spec to get ranked configs and an energy estimate.
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <section class="section-space">
        <h2 class="section-title">Pipeline</h2>
        <div class="flow-line">job spec -> feature build -> model score -> ranked configs -> selected run plan</div>
    </section>
    """,
    unsafe_allow_html=True,
)
