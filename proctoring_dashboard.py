# proctoring_dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="AI Proctoring Dashboard", layout="wide")
st.title("📊 Exam Proctoring Analytics Dashboard")

# Check if exam data exists
if "violation_list" not in st.session_state or len(st.session_state.violation_list) == 0:
    st.warning("⚠️ No exam data available. Start an exam first.")
    st.stop()

# Get analytics data
analytics = st.session_state.get("analytics", {})
violations = st.session_state.violation_list
violation_counts = analytics.get("violation_counts", {})

# ==================== TOP METRICS ==================== #
st.markdown("## 📈 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("🚨 Total Violations", len(violations))
with col2:
    st.metric("🔴 High Severity", sum(1 for v in violations if v["severity"] == "HIGH"))
with col3:
    st.metric("🟡 Medium Severity", sum(1 for v in violations if v["severity"] == "MEDIUM"))
with col4:
    st.metric("📋 Copy/Paste Attempts", analytics.get("copy_paste_attempts", 0))
with col5:
    st.metric("📑 Tab Switches", analytics.get("tab_switches", 0))

st.divider()

# ==================== VIOLATION TIMELINE ==================== #
st.markdown("## 📜 Violation Timeline")

if violations:
    timeline_data = []
    for i, v in enumerate(violations):
        timeline_data.append({
            "Time": v["timestamp"],
            "Violation": v["reason"],
            "Severity": v["severity"],
            "Evidence": v.get("evidence", "N/A")
        })
    
    df_timeline = pd.DataFrame(timeline_data)
    st.dataframe(df_timeline, use_container_width=True)

st.divider()

# ==================== VIOLATION BREAKDOWN CHART ==================== #
st.markdown("## 📊 Violation Analysis")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("### Violations by Type")
    if violation_counts:
        violation_types = list(violation_counts.keys())
        violation_counts_list = list(violation_counts.values())
        
        if PLOTLY_AVAILABLE:
            fig = go.Figure(data=[
                go.Bar(x=violation_types, y=violation_counts_list, marker_color='indianred')
            ])
            fig.update_layout(
                title="Violation Count by Type",
                xaxis_title="Violation Type",
                yaxis_title="Count",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            chart_df = pd.DataFrame({"Type": violation_types, "Count": violation_counts_list})
            st.bar_chart(chart_df.set_index("Type"))

with col_chart2:
    st.markdown("### Severity Distribution")
    severity_counts = {
        "HIGH": sum(1 for v in violations if v["severity"] == "HIGH"),
        "MEDIUM": sum(1 for v in violations if v["severity"] == "MEDIUM")
    }
    
    if PLOTLY_AVAILABLE:
        fig = go.Figure(data=[
            go.Pie(
                labels=list(severity_counts.keys()),
                values=list(severity_counts.values()),
                marker=dict(colors=['red', 'orange'])
            )
        ])
        fig.update_layout(
            title="Severity Distribution",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        severity_df = pd.DataFrame({"Severity": list(severity_counts.keys()), "Count": list(severity_counts.values())})
        st.bar_chart(severity_df.set_index("Severity"))

st.divider()

# ==================== DETAILED VIOLATIONS TABLE ==================== #
st.markdown("## 🔍 Detailed Violation Log")

# Create detailed table
detailed_violations = []
for v in violations:
    detailed_violations.append({
        "Timestamp": v["timestamp"],
        "Type": v["reason"],
        "Severity": "🔴" if v["severity"] == "HIGH" else "🟡",
        "Evidence File": os.path.basename(v.get("evidence", "N/A"))
    })

df_detailed = pd.DataFrame(detailed_violations)
st.dataframe(df_detailed, use_container_width=True)

st.divider()

# ==================== ACTIVITY METRICS ==================== #
st.markdown("## 🎯 Activity Metrics")

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("🖱️ Mouse Clicks", analytics.get("mouse_clicks", 0))
with col_m2:
    st.metric("⌨️ Keyboard Activity", "Active")
with col_m3:
    st.metric("🌐 Inactivity Periods", analytics.get("inactivity_periods", 0))

st.divider()

# ==================== EVIDENCE SECTION ==================== #
st.markdown("## 📸 Evidence Gallery")

evidence_screenshots = []
if os.path.exists("evidence/screenshots"):
    for img in sorted(os.listdir("evidence/screenshots")):
        if img.endswith(".png"):
            evidence_screenshots.append(f"evidence/screenshots/{img}")

if evidence_screenshots:
    cols = st.columns(4)
    for idx, img_path in enumerate(evidence_screenshots[-12:]):  # Show last 12
        with cols[idx % 4]:
            st.image(img_path, width=150, caption=os.path.basename(img_path))
else:
    st.info("No evidence screenshots available")

st.divider()

# ==================== EXAM SUMMARY ==================== #
st.markdown("## 📋 Exam Summary")

summary_text = f"""
**Exam Date & Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Total Violations Detected**: {len(violations)}

**Critical Alerts**: {sum(1 for v in violations if v["severity"] == "HIGH")}

**Most Common Violation**: {max(violation_counts, key=violation_counts.get) if violation_counts else "None"}

**Recommendation**: {'⚠️ Suspicious Activity Detected - Review Evidence' if len(violations) > 3 else '✅ Normal Exam Conduct'}
"""

st.info(summary_text)

# Export button
if st.button("📥 Export Report as CSV"):
    csv_data = df_detailed.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=f"exam_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
