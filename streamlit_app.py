import streamlit as st
from datetime import datetime, timedelta
import random
import pandas as pd

# ===== Core Logic =====

def simulate_with_helps1(effective_seconds, speed_boost_percent, guild_helps):
    speed_multiplier = 1 + speed_boost_percent / 100.0
    remaining = effective_seconds / speed_multiplier

    for _ in range(guild_helps):
        reduction = max(remaining * 0.01, 60)  # simulate help delay
        delay = random.uniform(40, 60)
        remaining -= (reduction + delay)
        if remaining <= 0:
            return 0
    return remaining


def simulate_with_helps(effective_seconds, guild_helps):
    remaining = effective_seconds
    for _ in range(guild_helps):
        reduction = max(remaining * 0.01, 60)
        delay = random.uniform(40, 60)
        remaining -= (reduction + delay)
        if remaining <= 60:
            remaining = 0
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

st.set_page_config(page_title="TopHero Time Estimator", page_icon="⏳")
st.title("⏳ TopHero Time Estimation Tool")

st.warning("""
🚧 **Unofficial Tool – Experimental Version**

This tool is **not affiliated with the official game** and is currently in an experimental stage.  
Some calculations (especially guild help effects) may differ slightly due to **hidden in-game mechanics** and the timing of guild helps.

📬 If you have any questions, feel free to reach out to me in **10400** — `1V333S`.
""")

# === Tabs Layout ===
tab1, tab2, tab3, tab4= st.tabs([
    "📖 ReadMe & Contact",
    "📊 Max Healing Time",
    "👑 Completion Comparison",
    "📈 Tech Power Efficiency"
])

with tab1:
    st.markdown("## 📖 About This Tool")
    st.markdown("""
    This is an unofficial estimation tool for **TopHeroes** healing and tech optimization.
    
    **Purpose:**
    - Maximize troop healing before War Day.
    - Compare how Title Boost affects your completion time.
    - Evaluate which tech gives the best power gain per hour during tech events.

    ---
    ## 📬 Contact

    - Discord: **`ivesliu`** 
    - TopHeroes: **`1V333S`** in server **`10400`**
    """)


with tab2:
    st.markdown("""
    ### 🏥 Max Hospital Time Before War Day
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

with tab3:
    st.markdown("""
    ### 📅 Completion Time Comparison With and Without Title Boost
    Calculate when a task would finish based on your start time and boost, and how much faster it would be with an extra +10% title boost.

    _Note: Due to the randomness in guild help timing, the results may slightly vary on each run.  
    By default, this tool assumes an **average delay of 15 seconds** per help action._
    """)

    st.subheader("⏰ Completion Time Comparison")

    col1, col2 = st.columns(2)

    with col1:
        start_date2 = st.date_input("Start Date (Boosted Timer)", key="start_date2")
        timer_days = st.number_input("Start Timer Days", 0, 30, 1)
        timer_hours = st.number_input("Start Timer Hours", 0, 23, 0)
        timer_minutes = st.number_input("Start Timer Minutes", 0, 59, 0)
        timer_seconds = st.number_input("Start Timer Seconds", 0, 59, 0)
        current_boost = st.number_input("Current Boost (%)", 0, 500, 110)

    with col2:
        start_time2 = st.time_input("Start Time (Boosted Timer)", key="start_time2")
        title_bonus = st.number_input("Title Boost (%)", 0, 100, 10)
        free_speedup_minutes_2 = st.number_input("Free Speedup (minutes)", 0, 60, 5, key="fs2")
        free_speedup_extra_seconds_2 = st.number_input("Free Speedup (extra seconds)", 0, 59, 0, key="fs2s")
        guild_helps_2 = st.number_input("Guild Helps", 0, 100, 20, key="gh_title")

    if st.button("📅 Estimate Completion Time"):
        base_seconds = timer_days * 86400 + timer_hours * 3600 + timer_minutes * 60 + timer_seconds

        # Without title
        before_helps_no_title = base_seconds
        after_helps_no_title = simulate_with_helps(before_helps_no_title, guild_helps_2)
        finish_no_title = datetime.combine(start_date2, start_time2) + timedelta(seconds=after_helps_no_title)

        # With title
        boost_with_title = current_boost + title_bonus
        before_helps_with_title = base_seconds * (1 + current_boost / 100.0) / (1 + boost_with_title / 100.0)
        after_helps_with_title = simulate_with_helps(before_helps_with_title, guild_helps_2)
        finish_with_title = datetime.combine(start_date2, start_time2) + timedelta(seconds=after_helps_with_title)

        st.subheader("🕒 Completion Estimate")
        st.markdown(f"**⏳ Without Title - Before Helps:** `{format_time(before_helps_no_title)}` → `{(datetime.combine(start_date2, start_time2) + timedelta(seconds=before_helps_no_title)).strftime('%Y-%m-%d %H:%M:%S')}`")
        st.markdown(f"**✅ Without Title - After Helps:** `{format_time(after_helps_no_title)}` → `{finish_no_title.strftime('%Y-%m-%d %H:%M:%S')}`")

        time_saved_no_title = before_helps_no_title - after_helps_no_title
        d1 = int(time_saved_no_title // 86400)
        h1 = int((time_saved_no_title % 86400) // 3600)
        m1 = int((time_saved_no_title % 3600) // 60)
        s1 = int(time_saved_no_title % 60)
        st.info(f"📉 Time Saved from Helps (without Title): `{d1}d {h1:02d}:{m1:02d}:{s1:02d}`")

        st.markdown(f"**👑 With Title - Before Helps:** `{format_time(before_helps_with_title)}` → `{(datetime.combine(start_date2, start_time2) + timedelta(seconds=before_helps_with_title)).strftime('%Y-%m-%d %H:%M:%S')}`")
        st.markdown(f"**✅ With Title - After Helps:** `{format_time(after_helps_with_title)}` → `{finish_with_title.strftime('%Y-%m-%d %H:%M:%S')}`")

        time_saved_with_title = before_helps_with_title - after_helps_with_title
        d2 = int(time_saved_with_title // 86400)
        h2 = int((time_saved_with_title % 86400) // 3600)
        m2 = int((time_saved_with_title % 3600) // 60)
        s2 = int(time_saved_with_title % 60)
        st.info(f"📉 Time Saved from Helps (with Title): `{d2}d {h2:02d}:{m2:02d}:{s2:02d}`")

        time_diff = finish_no_title - finish_with_title
        diff_seconds = int(time_diff.total_seconds())
        d = diff_seconds // 86400
        h = (diff_seconds % 86400) // 3600
        m = (diff_seconds % 3600) // 60
        s = diff_seconds % 60
        st.warning(f"⏰ Time Saved With Title: `{d}d {h:02d}:{m:02d}:{s:02d}`")

        
with tab4:
    st.markdown("### 🧠 Tech Efficiency Comparison")
    st.markdown("Select multiple tech upgrades and compare which gives you the most power gain **per hour** with guild helps.")

    if "tech_names" not in st.session_state:
        st.session_state.tech_names = [f"Tech {i+1}" for i in range(2)]

    if st.button("➕ Add New Tech"):
        st.session_state.tech_names.append(f"Tech {len(st.session_state.tech_names) + 1}")

    num_techs = len(st.session_state.tech_names)
    helps = st.number_input("Expected Guild Helps", 0, 100, 20, key="eff_helps")

    tech_data = []
    for i in range(num_techs):
        col_exp, col_del = st.columns([9, 1])  # 90% expander, 10% button
        with col_exp:
            with st.expander(f"⚙️ {st.session_state.tech_names[i]}", expanded=(i == 0)):
                name = st.text_input("Tech Name", key=f"name_{i}")
                if name:
                    st.session_state.tech_names[i] = name

                power = st.number_input("Power Gain", 0, 100000, 3000, key=f"power_{i}")

                col1, col2, col3, col4 = st.columns(4)
                days = col1.number_input("Days", 0, 30, 0, key=f"day_{i}")
                hours = col2.number_input("Hours", 0, 23, 0, key=f"hour_{i}")
                minutes = col3.number_input("Minutes", 0, 59, 0, key=f"min_{i}")
                seconds = col4.number_input("Seconds", 0, 59, 0, key=f"sec_{i}")

                tech_data.append({
                    "name": name or f"Tech {i + 1}",
                    "power": power,
                    "duration": timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
                })

        with col_del:
            if st.button("❌", key=f"remove_{i}"):
                st.session_state.tech_names.pop(i)
                st.rerun()


    if st.button("🚀 Compare Efficiency"):
        results = []
        for entry in tech_data:
            secs = entry["duration"].total_seconds()
            if secs == 0:
                continue
            secs_after = simulate_with_helps(secs, helps)
            power = entry["power"]
            ph_before = power / (secs / 3600)
            ph_after = power / (secs_after / 3600) if secs_after else float("inf")
            gain = (ph_after - ph_before) / ph_before * 100 if ph_before else 0
            results.append({
                "Tech": entry["name"],
                "Power": power,
                "Time Before Helps": format_time(secs),
                "Time After Helps": format_time(secs_after),
                "Power/hr Before": round(ph_before, 2),
                "Power/hr After": round(ph_after, 2),
                "Efficiency Gain (%)": round(gain, 2)
            })

        st.markdown("### 📊 Efficiency Comparison")
        st.dataframe(results, use_container_width=True)


