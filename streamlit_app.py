import streamlit as st
from datetime import datetime, timedelta

# ===== Core Logic =====

def simulate_with_helps1(effective_seconds, speed_boost_percent, guild_helps):
    speed_multiplier = 1 + speed_boost_percent / 100.0
    remaining = effective_seconds / speed_multiplier

    for _ in range(guild_helps):
        reduction = max(remaining * 0.01, 60) - 30  # simulate help delay
        remaining -= reduction
        if remaining <= 0:
            return 0
    return remaining

def simulate_with_helps(effective_seconds, guild_helps):
    remaining = effective_seconds
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

        remaining = simulate_with_helps1(effective, speed_boost_percent, guild_helps)

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

st.set_page_config(page_title="Castle Build Time Estimator", page_icon="⏳")
st.title("⏳ TopHero Time Tool")

st.warning("""
🚧 **Unofficial Tool – Experimental Version**

This tool is **not affiliated with the official game** and is currently in an experimental stage.  
Some calculations (especially guild help effects) may differ slightly due to **hidden in-game mechanics** and the timing of guild helps.

✅ For now, we recommend using **Feature 1** to estimate how much troop healing time you can fit before War Day reset.
""")

# === Tabs Layout ===
tab1, tab2 = st.tabs(["📊 Max Healing Time", "👑 Completion Comparison"])

with tab1:
    st.markdown("""
    ### 🏥 Feature 1: Max Hospital Time Before War Day
    Calculate the **maximum troop healing duration** that will finish **before War Day reset**, based on speed boost, free speedup, and expected guild helps. 
    Use this to optimize your hospital usage and **maximize points** on War Day.
    """)
    
    st.markdown("***Send troops to the hospital until the Start Time showed on your botton***")

    now = datetime.now()
    if "start_time" not in st.session_state:
        st.session_state.start_time = now.time()
    if "end_time" not in st.session_state:
        st.session_state.end_time = (now + timedelta(days=8)).time()
    if "start_date" not in st.session_state:
        st.session_state.start_date = now.date()
    if "end_date" not in st.session_state:
        st.session_state.end_date = (now + timedelta(days=8)).date()

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

    st.subheader("⚙️ Build Settings")
    guild_helps = st.number_input("Expected Guild Helps", 0, 100, 20)
    speed_boost_percent = st.number_input("Healing Speed Boost (%)", 0, 500, 110)
    # free_speedup_minutes = st.number_input("Free Speedup (minutes)", 0, 60, 5)
    free_speedup_minutes = 0
    free_speedup_seconds = free_speedup_minutes * 60

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

            # st.success(f"🧱 Maximum Original Build Time: `{format_time(max_build_seconds)}`")
            st.info(f"⏳ Start Time: `{format_time(start_seconds)}`")

with tab2:
    st.markdown("""
    ### 📅 Feature 2: Completion Time Comparison With and Without Title Boost
    Calculate when a task would finish based on your start time and boost, and how much faster it would be with an extra +10% title boost.
    """)

    st.subheader(":alarm_clock: Completion Time Comparison")

    start_date2 = st.date_input("Start Date (Boosted Timer)", key="start_date2")
    start_time2 = st.time_input("Start Time (Boosted Timer)", key="start_time2")
    start_datetime = datetime.combine(start_date2, start_time2)

    timer_days = st.number_input("Start Timer Days", 0, 30, 1)
    timer_hours = st.number_input("Start Timer Hours", 0, 23, 0)
    timer_minutes = st.number_input("Start Timer Minutes", 0, 59, 0)
    timer_seconds = st.number_input("Start Timer Seconds", 0, 59, 0)
    current_boost = st.number_input("Current Boost (%)", 0, 500, 110)
    title_bonus = st.number_input("Title Boost (%)", 0, 100, 10)
    free_speedup_minutes_2 = st.number_input("Free Speedup (minutes)", 0, 60, 5, key="fs2")
    free_speedup_extra_seconds_2 = st.number_input("Free Speedup (extra seconds)", 0, 59, 0, key="fs2s")
    free_speedup_seconds_2 = free_speedup_minutes_2 * 60 + free_speedup_extra_seconds_2
    guild_helps_2 = st.number_input("Guild Helps", 0, 100, 20, key="gh_title")

    if st.button(":abacus: Estimate Completion Time"):
        base_seconds = timer_days * 86400 + timer_hours * 3600 + timer_minutes * 60 + timer_seconds

        # Without title
        before_helps_no_title = base_seconds
        after_helps_no_title = simulate_with_helps(
            before_helps_no_title,
            guild_helps_2)

        finish_no_title = start_datetime + timedelta(seconds=after_helps_no_title)

        # With title
        boost_with_title = current_boost + title_bonus
        before_helps_with_title = base_seconds * (1 + current_boost / 100.0) / (1 + boost_with_title / 100.0)
        after_helps_with_title = simulate_with_helps(
            before_helps_with_title,
            guild_helps_2)
        finish_with_title = start_datetime + timedelta(seconds=after_helps_with_title)

        st.subheader("🕒 Completion Estimate")
        st.markdown(f"**⏳ Without Title - Before Helps:** `{format_time(before_helps_no_title)}` → `{(start_datetime + timedelta(seconds=before_helps_no_title)).strftime('%Y-%m-%d %H:%M:%S')}`")
        st.markdown(f"**✅ Without Title - After Helps:** `{format_time(after_helps_no_title)}` → `{finish_no_title.strftime('%Y-%m-%d %H:%M:%S')}`")
        st.markdown(f"**👑 With Title - Before Helps:** `{format_time(before_helps_with_title)}` → `{(start_datetime + timedelta(seconds=before_helps_with_title)).strftime('%Y-%m-%d %H:%M:%S')}`")
        st.markdown(f"**✅ With Title - After Helps:** `{format_time(after_helps_with_title)}` → `{finish_with_title.strftime('%Y-%m-%d %H:%M:%S')}`")

        # Difference summary
        time_diff = (finish_no_title - finish_with_title)
        diff_seconds = int(time_diff.total_seconds())
        d = diff_seconds // 86400
        h = (diff_seconds % 86400) // 3600
        m = (diff_seconds % 3600) // 60
        s = diff_seconds % 60

        st.warning(f"⏰ Time Saved With Title: `{d}d {h:02d}:{m:02d}:{s:02d}`")