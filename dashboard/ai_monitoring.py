
import pandas as pd
import streamlit as st

from src.agents.ai_metrics import (
    calculate_ai_metrics,
    load_audit_events,
)


st.set_page_config(
    page_title="PharmaFlow AI Monitoring",
    page_icon="📊",
    layout="wide",
)

st.title("PharmaFlow AI Monitoring")
st.caption(
    "Local observability dashboard for Agentic AI "
    "analytics tool executions."
)


def load_monitoring_data():
    """Read the latest persisted audit events."""
    events = load_audit_events()
    metrics = calculate_ai_metrics(events)
    return events, metrics


if st.button("Refresh metrics"):
    st.rerun()


events, metrics = load_monitoring_data()

if not events:
    st.info(
        "No AI audit events found yet. "
        "Run an AI analytics question to generate events."
    )

st.subheader("AI Execution Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Executions",
        metrics["total_executions"],
    )

with col2:
    st.metric(
        "Success Rate",
        f'{metrics["success_rate"]:.2f}%',
    )

with col3:
    st.metric(
        "Failed Executions",
        metrics["failed_executions"],
    )

with col4:
    st.metric(
        "Average Duration",
        f'{metrics["average_duration_ms"]:.2f} ms',
    )


st.divider()
st.subheader("Tool Execution Breakdown")

tool_rows = []

for tool_name, values in metrics["tools"].items():
    tool_rows.append({
        "Tool": tool_name,
        "Executions": values["executions"],
        "Successes": values["successes"],
        "Failures": values["failures"],
    })

tool_df = pd.DataFrame(tool_rows)

st.dataframe(
    tool_df,
    use_container_width=True,
    hide_index=True,
)

if not tool_df.empty:
    st.bar_chart(
        tool_df.set_index("Tool")[
            ["Successes", "Failures"]
        ]
    )


st.divider()
st.subheader("Recent Audit Events")

if events:
    event_df = pd.DataFrame(events)

    event_df = event_df.rename(
        columns={
            "timestamp": "Timestamp (UTC)",
            "tool": "Tool",
            "status": "Status",
            "duration_ms": "Duration (ms)",
        }
    )

    event_df = event_df.sort_values(
        "Timestamp (UTC)",
        ascending=False,
    )

    st.dataframe(
        event_df.head(50),
        use_container_width=True,
        hide_index=True,
    )

else:
    st.write("No audit events available.")


st.divider()
st.caption(
    "PharmaFlow AI Monitoring | "
    "Local audit metadata only | "
    "No user questions or analytics results stored"
)
