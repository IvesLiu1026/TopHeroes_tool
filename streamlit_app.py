import streamlit as st
from datetime import datetime, timedelta

# ===== Core Logic =====

def simulate_with_helps(effective_seconds, speed_boost_percent, guild_helps):
    speed_multiplier = 1 + speed_boost_percent / 100.0
    remaining = effective_seconds / speed_multiplier

    for _ in range(guild_helps):
        reduction = max(remaining * 0.01, 60) - 30  # simulate help delay
        remaining -= reduction
        if remaining <= 0:
            return 0
    return remaining

def max_build_time_within_target_seconds(target_seconds,
                                         guild_helps, speed_boost_percent,
                                         free_speedup_seconds=300, precision=1):
    low = 0
    high = target_seconds * 5
    best_fit = 0

    while low <= high:
        mid = (low + high) // 2
        effective = mid - free_speedup_seconds
        if effective <= 0:
            high = mid - 1
            continue

        remaining = simulate_with_helps(effective, speed_boost_percent, guild_helps)

        if remaining <= target_seconds:
            best_fit = mid
            low = mid + precision
        else:
            high = mid - precision

    return best_fit

def format_time(seconds):
    d = int(seconds // 86400)
    h = int((seconds % 86400) // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{d}d {h:02d}:{m:02d}:{s:02d}"

# ===== Streamlit App =====

st.set_page_config(page_title="Castle Build Time Estimator", page_icon="⌛")

st.title("⌛ Time Estimator")
st.markdown(
    "Calculate the **maximum original build time** that can be completed on time "
    "given your speed boost, free speedup, and expected guild helps."
)

# Initialize session state to remember user input (prevent reset)
now = datetime.now()
if "start_time" not in st.session_state:
    st.session_state.start_time = now.time()
if "end_time" not in st.session_state:
    st.session_state.end_time = (now + timedelta(days=8)).time()
if "start_date" not in st.session_state:
    st.session_state.start_date = now.date()
if "end_date" not in st.session_state:
    st.session_state.end_date = (now + timedelta(days=8)).date()

# === Target Time Section ===
st.subheader("🎯 Target Completion Window")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=st.session_state.start_date, key="start_date")
    start_time = st.time_input("Start Time", value=st.session_state.start_time, key="start_time")
with col2:
    end_date = st.date_input("End Date", value=st.session_state.end_date, key="end_date")
    end_time = st.time_input("End Time", value=st.session_state.end_time, key="end_time")

start_dt = datetime.combine(start_date, start_time)
end_dt = datetime.combine(end_date, end_time)
target_delta = end_dt - start_dt
target_seconds = int(target_delta.total_seconds())

# === Build Parameters Section ===
st.subheader("⚙️ Build Settings")

guild_helps = st.number_input("Expected Guild Helps", 0, 100, 20)
speed_boost_percent = st.number_input("Speed Boost (%)", 0, 500, 110)
free_speedup_minutes = st.number_input("Free Speedup (minutes)", 0, 60, 5)
free_speedup_seconds = free_speedup_minutes * 60

# === Run Calculation ===
if st.button("Calculate 🔍"):
    if target_seconds <= 0:
        st.error("⛔ End time must be later than start time.")
    else:
        max_build_seconds = max_build_time_within_target_seconds(
            target_seconds, guild_helps, speed_boost_percent, free_speedup_seconds
        )

        effective = max_build_seconds - free_speedup_seconds
        speed_multiplier = 1 + speed_boost_percent / 100.0
        start_seconds = effective / speed_multiplier

        st.success(f"🧱 Maximum Original Build Time: `{format_time(max_build_seconds)}`")
        st.info(f"⏳ Start Timer (with boost only, no helps): `{format_time(start_seconds)}`")
