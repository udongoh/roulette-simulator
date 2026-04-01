import streamlit as st
import secrets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Roulette Simulator", page_icon="\U0001F3B0", layout="centered")

RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

BOARD_ROWS = [
    [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
    [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
    [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
]

def get_color(n):
    if n == 0 or n == -1:
        return "green"
    return "red" if n in RED_NUMBERS else "black"

def get_display(n):
    return "00" if n == -1 else str(n)

def spin_wheel(variant):
    pockets = list(range(0, 37)) + ([-1] if variant == "American" else [])
    return secrets.choice(pockets)

def evaluate_bet(bet_type, bet_numbers, result, variant):
    total = 38 if variant == "American" else 37
    win = result in bet_numbers
    payout_map = {
        "straight": 35, "red": 1, "black": 1, "odd": 1, "even": 1,
        "low": 1, "high": 1, "dozen": 2, "column": 2,
    }
    payout = payout_map.get(bet_type, 0)
    pw = len(bet_numbers) / total
    return win, payout, pw

def get_bet_numbers(bet_type, bet_value, variant):
    if bet_type == "straight":
        return [bet_value]
    elif bet_type == "red":
        return list(RED_NUMBERS)
    elif bet_type == "black":
        return list(BLACK_NUMBERS)
    elif bet_type == "odd":
        return [n for n in range(1, 37) if n % 2 == 1]
    elif bet_type == "even":
        return [n for n in range(1, 37) if n % 2 == 0]
    elif bet_type == "low":
        return list(range(1, 19))
    elif bet_type == "high":
        return list(range(19, 37))
    elif bet_type == "dozen":
        start = (bet_value - 1) * 12 + 1
        return list(range(start, start + 12))
    elif bet_type == "column":
        return [n for n in range(1, 37) if n % 3 == (bet_value % 3)]
    return []

def place_bet(bet_type, numbers, label):
    st.session_state.bets.append({
        "type": bet_type, "numbers": numbers,
        "label": label, "amount": st.session_state.chip_size
    })

for key, default in [("bets", []), ("balance", 1000), ("session_log", []),
                      ("last_result", None), ("chip_size", 10)]:
    if key not in st.session_state:
        st.session_state[key] = default

selected_nums = set()
for b in st.session_state.bets:
    for n in b["numbers"]:
        selected_nums.add(n)

def btn_style(num):
    if num in RED_NUMBERS:
        bg, hover = "#C62828", "#E53935"
    elif num in BLACK_NUMBERS:
        bg, hover = "#212121", "#424242"
    else:
        bg, hover = "#2E7D32", "#388E3C"
    border = "3px solid #FFD700" if num in selected_nums else "1px solid #8D6E63"
    shadow = "0 0 8px #FFD700" if num in selected_nums else "none"
    hit = ""
    if st.session_state.last_result is not None and st.session_state.last_result == num:
        border = "3px solid #FFD700"
        shadow = "0 0 14px #FFD700"
        hit = "animation: pulse 1s ease-in-out infinite;"
    return bg, hover, border, shadow, hit

st.markdown("""
<style>
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}
div.stButton > button {
    height: 54px;
    font-weight: bold;
    font-size: 18px;
    border-radius: 8px;
    transition: all 0.15s;
    padding: 8px 4px;
    min-width: 44px;
}
.board-container {
    background: #1B5E20;
    border: 3px solid #FFD700;
    border-radius: 12px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Settings")
    variant = st.selectbox("Variant", ["European (37)", "American (38)"])
    variant_key = "American" if "American" in variant else "European"
    st.session_state.chip_size = st.select_slider(
        "Chip Size ($)", options=[1, 5, 10, 25, 50, 100, 500],
        value=st.session_state.chip_size)
    new_bal = st.number_input("Starting Balance ($)", 10, 1000000,
                               st.session_state.balance, step=100)
    if new_bal != st.session_state.balance and not st.session_state.session_log:
        st.session_state.balance = new_bal
    st.divider()
    if st.button("New Session", use_container_width=True):
        st.session_state.bets = []
        st.session_state.session_log = []
        st.session_state.last_result = None
        st.session_state.balance = 1000
        st.rerun()

st.markdown('<div class="board-container">', unsafe_allow_html=True)

hdr1, hdr2 = st.columns([2, 1])
with hdr1:
    st.markdown(f"<h3 style='color:#FFD700; margin:0;'>{variant_key} Roulette</h3>",
                unsafe_allow_html=True)
with hdr2:
    st.markdown(f"<h4 style='color:white; text-align:right; margin:0;'>Balance: ${st.session_state.balance:,}</h4>",
                unsafe_allow_html=True)

if st.session_state.last_result is not None:
    r = st.session_state.last_result
    c = get_color(r)
    emoji = {"red": "\U0001F534", "black": "\u26AB", "green": "\U0001F7E2"}.get(c, "")
    st.markdown(f"<p style='text-align:center; font-size:20px; color:#FFD700; margin:8px 0 4px 0;'>"
                f"Last: {emoji} <b>{get_display(r)}</b></p>", unsafe_allow_html=True)

all_numbers = ["0"] + (["00"] if variant_key == "American" else []) + [str(n) for n in range(1, 37)]
number_options = [f"{n} ({get_color(int(n) if n != '00' else -1).upper()})" for n in all_numbers]

picked_numbers = st.multiselect("Straight bets — pick one or more numbers", options=number_options, default=[], placeholder="Tap to select numbers...")

if picked_numbers:
    if st.button(f"Place {len(picked_numbers)} Straight Bet(s)", key="place_straight", use_container_width=True, type="primary"):
        for p in picked_numbers:
            raw = p.split(" (")[0]
            num_val = -1 if raw == "00" else int(raw)
            place_bet("straight", [num_val], raw)
        st.rerun()

st.markdown("---")
st.markdown("<p style='color:#FFD700; font-weight:bold; text-align:center; margin:4px 0;'>OUTSIDE BETS</p>",
            unsafe_allow_html=True)

oc1, oc2 = st.columns(2)
with oc1:
    if st.button("Red", key="bet_red", use_container_width=True, type="secondary"):
        place_bet("red", get_bet_numbers("red", None, variant_key), "Red")
        st.rerun()
with oc2:
    if st.button("Black", key="bet_black", use_container_width=True, type="secondary"):
        place_bet("black", get_bet_numbers("black", None, variant_key), "Black")
        st.rerun()

oc3, oc4 = st.columns(2)
with oc3:
    if st.button("Odd", key="bet_odd", use_container_width=True, type="secondary"):
        place_bet("odd", get_bet_numbers("odd", None, variant_key), "Odd")
        st.rerun()
with oc4:
    if st.button("Even", key="bet_even", use_container_width=True, type="secondary"):
        place_bet("even", get_bet_numbers("even", None, variant_key), "Even")
        st.rerun()

oc5, oc6 = st.columns(2)
with oc5:
    if st.button("1-18", key="bet_low", use_container_width=True, type="secondary"):
        place_bet("low", get_bet_numbers("low", None, variant_key), "1-18")
        st.rerun()
with oc6:
    if st.button("19-36", key="bet_high", use_container_width=True, type="secondary"):
        place_bet("high", get_bet_numbers("high", None, variant_key), "19-36")
        st.rerun()

dc1, dc2, dc3 = st.columns(3)
for col, key, label, val in [(dc1, "bet_d1", "1st 12", 1), (dc2, "bet_d2", "2nd 12", 2), (dc3, "bet_d3", "3rd 12", 3)]:
    with col:
        if st.button(label, key=key, use_container_width=True, type="secondary"):
            place_bet("dozen", get_bet_numbers("dozen", val, variant_key), label)
            st.rerun()

cc1, cc2, cc3 = st.columns(3)
for col, key, label, val in [(cc1, "bet_c1", "Col 1", 1), (cc2, "bet_c2", "Col 2", 2), (cc3, "bet_c3", "Col 3", 3)]:
    with col:
        if st.button(label, key=key, use_container_width=True, type="secondary"):
            place_bet("column", get_bet_numbers("column", val, variant_key), label)
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.bets:
    st.markdown("---")
    st.markdown("<p style='color:#FFD700; font-weight:bold; text-align:center; margin:4px 0;'>CURRENT BETS</p>",
                unsafe_allow_html=True)
    total_wagered = sum(b["amount"] for b in st.session_state.bets)
    bet_summary = {}
    for b in st.session_state.bets:
        key = b["label"]
        if key in bet_summary:
            bet_summary[key]["amount"] += b["amount"]
        else:
            bet_summary[key] = {"type": b["type"], "amount": b["amount"], "numbers": b["numbers"]}

    chips_html = '<div style="display:flex; flex-wrap:wrap; gap:6px; justify-content:center; margin:8px 0;">'
    for label, info in bet_summary.items():
        c = get_color(info["numbers"][0]) if info["type"] == "straight" else "brown"
        bgmap = {"red": "#C62828", "black": "#212121", "green": "#2E7D32", "brown": "#5D4037"}
        bg = bgmap.get(c, "#5D4037")
        chips_html += (f'<span style="background:{bg}; color:white; padding:5px 12px; '
                       f'border-radius:20px; font-weight:bold; border:2px solid #FFD700; '
                       f'font-size:13px;">{label} ${info["amount"]}</span>')
    chips_html += '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([1, 2, 1])
    with sc1:
        st.metric("Wagered", f"${total_wagered:,}")
    with sc2:
        if st.button("SPIN!", key="spin_btn", use_container_width=True, type="primary"):
            if total_wagered > st.session_state.balance:
                st.error("Not enough balance!")
            else:
                st.session_state.balance -= total_wagered
                result = spin_wheel(variant_key)
                st.session_state.last_result = result
                total_won = 0
                bet_details = []
                for label, b in bet_summary.items():
                    win, payout, pw = evaluate_bet(b["type"], b["numbers"], result, variant_key)
                    winnings = 0
                    if win:
                        winnings = b["amount"] * payout + b["amount"]
                        total_won += winnings
                    bet_details.append({
                        "label": label, "type": b["type"],
                        "amount": b["amount"], "win": win,
                        "payout": payout, "winnings": winnings, "pw": pw,
                    })
                st.session_state.balance += total_won
                net = total_won - total_wagered
                st.session_state.session_log.append({
                    "spin": len(st.session_state.session_log) + 1,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "result": get_display(result), "result_num": result,
                    "color": get_color(result), "total_wagered": total_wagered,
                    "total_won": total_won, "net": net,
                    "balance": st.session_state.balance,
                    "bet_details": bet_details,
                })
                st.session_state.bets = []
                st.rerun()
    with sc3:
        if st.button("Clear", key="clear_btn", use_container_width=True):
            st.session_state.bets = []
            st.rerun()

if st.session_state.session_log:
    last = st.session_state.session_log[-1]
    st.markdown("---")
    emoji = {"red": "\U0001F534", "black": "\u26AB", "green": "\U0001F7E2"}.get(last["color"], "")
    if last["net"] >= 0:
        st.success(f"{emoji} **{last['result']}** ({last['color'].upper()}) \u2014 WIN +${last['total_won']:,}  |  Balance: ${st.session_state.balance:,}")
    else:
        st.error(f"{emoji} **{last['result']}** ({last['color'].upper()}) \u2014 LOSS -${last['total_wagered']:,}  |  Balance: ${st.session_state.balance:,}")

    if len(st.session_state.session_log) >= 2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        fig.patch.set_facecolor("#0e1117")
        for ax in [ax1, ax2]:
            ax.set_facecolor("#16213e")
            ax.tick_params(colors="white")
            for s in ["top", "right"]:
                ax.spines[s].set_visible(False)
            for s in ["bottom", "left"]:
                ax.spines[s].set_color("white")

        init_bal = st.session_state.session_log[0]["balance"] - st.session_state.session_log[0]["net"]
        xs = [0] + [r["spin"] for r in st.session_state.session_log]
        ys = [init_bal] + [r["balance"] for r in st.session_state.session_log]
        ax1.plot(xs, ys, color="#00d4aa", linewidth=2, marker="o", markersize=3)
        ax1.fill_between(xs, ys, alpha=0.15, color="#00d4aa")
        ax1.axhline(y=init_bal, color="gray", linestyle="--", alpha=0.5)
        ax1.set_title("Balance", color="white", fontweight="bold")
        ax1.set_xlabel("Spin", color="white")
        ax1.set_ylabel("$", color="white")

        cumul = np.cumsum([r["net"] for r in st.session_state.session_log])
        sn = range(1, len(st.session_state.session_log) + 1)
        ax2.fill_between(sn, cumul, where=(cumul >= 0), color="#00d4aa", alpha=0.3)
        ax2.fill_between(sn, cumul, where=(cumul < 0), color="#ff4757", alpha=0.3)
        ax2.plot(sn, cumul, color="white", linewidth=1.5)
        ax2.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")
        ax2.set_title("Cumulative P&L", color="white", fontweight="bold")
        ax2.set_xlabel("Spin", color="white")
        ax2.set_ylabel("$", color="white")

        plt.tight_layout()
        st.pyplot(fig)

    st.subheader("Session History")
    log_html = """
    <style>
    .log-table { width:100%; border-collapse:collapse; font-size:13px; }
    .log-table th { background:#1a1a2e; color:#FFD700; padding:8px 6px; text-align:center; border-bottom:2px solid #FFD700; font-size:12px; }
    .log-table td { padding:7px 6px; text-align:center; border-bottom:1px solid #333; color:white; }
    .log-table tr:hover { background:#1a1a2e; }
    .result-circle { display:inline-block; width:28px; height:28px; border-radius:50%; line-height:28px; text-align:center; font-weight:bold; font-size:12px; color:white; border:2px solid #FFD700; }
    .win-icon { color:#00d4aa; font-weight:bold; font-size:16px; }
    .loss-icon { color:#ff4757; font-weight:bold; font-size:16px; }
    .bet-chip { display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold; margin:1px 2px; color:white; }
    .net-pos { color:#00d4aa; font-weight:bold; }
    .net-neg { color:#ff4757; font-weight:bold; }
    </style>
    <table class="log-table">
    <tr><th>#</th><th>Time</th><th>Result</th><th>Wagered</th><th>Win</th><th>Net</th><th>Balance</th><th>Bets</th></tr>
    """
    color_map = {"red": "#C62828", "black": "#212121", "green": "#2E7D32"}
    bet_color_map = {"straight": "#7B1FA2", "red": "#C62828", "black": "#212121",
                     "odd": "#5D4037", "even": "#5D4037", "low": "#1565C0",
                     "high": "#1565C0", "dozen": "#E65100", "column": "#00695C"}
    for r in st.session_state.session_log:
        bg = color_map.get(r["color"], "#333")
        result_html = f'<span class="result-circle" style="background:{bg};">{r["result"]}</span>'
        win_icon = '<span class="win-icon">' + "</span> <span class=\"win-icon\">".join(
            ["\u2714" if bd["win"] else "" for bd in r.get("bet_details", [])]) + '</span>'
        loss_icon = '<span class="loss-icon">' + "</span> <span class=\"loss-icon\">".join(
            ["\u2718" if not bd["win"] else "" for bd in r.get("bet_details", [])]) + '</span>'
        any_win = any(bd["win"] for bd in r.get("bet_details", []))
        icon = '<span class="win-icon">\u2714</span>' if any_win else '<span class="loss-icon">\u2718</span>'
        net_cls = "net-pos" if r["net"] >= 0 else "net-neg"
        net_str = f'+${r["net"]:,}' if r["net"] >= 0 else f'-${abs(r["net"]):,}'
        bets_html = ""
        for bd in r.get("bet_details", []):
            bc = bet_color_map.get(bd["type"], "#5D4037")
            win_mark = "\u2714" if bd["win"] else "\u2718"
            bets_html += f'<span class="bet-chip" style="background:{bc};">{win_mark} {bd["label"]} ${bd["amount"]}</span> '
        time_str = r.get("time", "")
        log_html += f'<tr><td>{r["spin"]}</td><td>{time_str}</td><td>{result_html}</td>'
        log_html += f'<td>${r["total_wagered"]:,}</td><td>{icon}</td>'
        log_html += f'<td class="{net_cls}">{net_str}</td><td>${r["balance"]:,}</td>'
        log_html += f'<td style="text-align:left;">{bets_html}</td></tr>'
    log_html += '</table>'
    st.markdown(log_html, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Session Statistics")

    ts = len(st.session_state.session_log)
    tw = sum(1 for r in st.session_state.session_log if r["net"] > 0)
    tl = ts - tw
    tn = sum(r["net"] for r in st.session_state.session_log)
    total_wagered_all = sum(r["total_wagered"] for r in st.session_state.session_log)
    total_won_all = sum(r["total_won"] for r in st.session_state.session_log)
    actual_return = (total_won_all / total_wagered_all * 100) if total_wagered_all > 0 else 0
    house_edge = 5.26 if variant_key == "American" else 2.70
    expected_return = 100 - house_edge

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Spins", ts)
    m2.metric("Wins / Losses", f"{tw} / {tl}")
    m3.metric("Win Rate", f"{tw/ts*100:.1f}%")
    m4.metric("Net P&L", f"${tn:+,}")

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("Total Wagered", f"${total_wagered_all:,}")
    m6.metric("Total Returned", f"${total_won_all:,}")
    m7.metric("Your Return %", f"{actual_return:.1f}%", delta=f"{actual_return - expected_return:+.1f}% vs expected", delta_color="normal")
    m8.metric("House Edge", f"{house_edge:.2f}%")

    if ts >= 3:
        streak_type = None
        streak_len = 0
        max_win_streak = 0
        max_loss_streak = 0
        cur_streak = 0
        for r in st.session_state.session_log:
            if r["net"] > 0:
                if cur_streak > 0:
                    cur_streak += 1
                else:
                    cur_streak = 1
                max_win_streak = max(max_win_streak, cur_streak)
            else:
                if cur_streak < 0:
                    cur_streak -= 1
                else:
                    cur_streak = -1
                max_loss_streak = max(max_loss_streak, abs(cur_streak))

        biggest_win = max(r["net"] for r in st.session_state.session_log)
        biggest_loss = min(r["net"] for r in st.session_state.session_log)
        avg_bet = total_wagered_all / ts

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Best Win Streak", f"{max_win_streak} spins")
        s2.metric("Worst Loss Streak", f"{max_loss_streak} spins")
        s3.metric("Biggest Win", f"${biggest_win:+,}")
        s4.metric("Biggest Loss", f"${biggest_loss:+,}")

    with st.expander("Educational Insights", expanded=(ts <= 5)):
        st.markdown(f"""
**How Roulette Math Works:**

| Concept | {variant_key} Wheel |
|---|---|
| Total pockets | {'38 (0 and 00)' if variant_key == 'American' else '37 (single 0)'} |
| House edge | **{house_edge:.2f}%** per bet |
| Expected return | **{expected_return:.1f}%** of every dollar wagered |
| Your actual return | **{actual_return:.1f}%** over {ts} spin(s) |

**Key Takeaways:**
- The house edge means for every **$100 wagered**, you lose **${house_edge:.2f} on average** over time.
- {"The American wheel has **two** zero pockets (0 and 00), nearly doubling the house edge vs European." if variant_key == "American" else "The European wheel has **one** zero pocket, giving it the lowest standard house edge."}
- Short sessions can show big swings (variance), but over hundreds of spins, results converge toward the house edge. This is the **Law of Large Numbers**.
- No betting strategy changes the house edge — every spin is independent (**Gambler's Fallacy**).
""")

        if ts >= 2:
            st.markdown(f"""
**Your Session vs. Theory:**
- You wagered **${total_wagered_all:,}** across **{ts}** spins.
- **Expected loss**: ${total_wagered_all * house_edge / 100:,.0f} (house edge x total wagered)
- **Actual P&L**: ${tn:+,} — you're {"**ahead** of expectation (short-term luck!)" if tn > -(total_wagered_all * house_edge / 100) else "**tracking near** expected loss" if abs(tn + total_wagered_all * house_edge / 100) < total_wagered_all * 0.05 else "**behind** expectation (unlucky stretch)"}.
""")

    all_bet_details = []
    for r in st.session_state.session_log:
        for bd in r.get("bet_details", []):
            all_bet_details.append(bd)

    if all_bet_details:
        with st.expander("Bet Type Breakdown"):
            bet_type_stats = {}
            for bd in all_bet_details:
                bt = bd["type"]
                if bt not in bet_type_stats:
                    bet_type_stats[bt] = {"count": 0, "wins": 0, "wagered": 0, "returned": 0, "pw": bd["pw"]}
                bet_type_stats[bt]["count"] += 1
                bet_type_stats[bt]["wagered"] += bd["amount"]
                if bd["win"]:
                    bet_type_stats[bt]["wins"] += 1
                    bet_type_stats[bt]["returned"] += bd["winnings"]

            rows = []
            for bt, s in bet_type_stats.items():
                actual_wr = s["wins"] / s["count"] * 100 if s["count"] > 0 else 0
                expected_wr = s["pw"] * 100
                ret_pct = s["returned"] / s["wagered"] * 100 if s["wagered"] > 0 else 0
                rows.append({
                    "Bet Type": bt.capitalize(),
                    "# Bets": s["count"],
                    "Wins": s["wins"],
                    "Your Win %": f"{actual_wr:.1f}%",
                    "Expected Win %": f"{expected_wr:.1f}%",
                    "Wagered": f"${s['wagered']:,}",
                    "Returned": f"${s['returned']:,}",
                    "Return %": f"{ret_pct:.1f}%",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    result_counts = {"red": 0, "black": 0, "green": 0}
    for r in st.session_state.session_log:
        result_counts[r["color"]] = result_counts.get(r["color"], 0) + 1

    with st.expander("Result Distribution"):
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Red", f"{result_counts['red']} ({result_counts['red']/ts*100:.0f}%)")
        rc2.metric("Black", f"{result_counts['black']} ({result_counts['black']/ts*100:.0f}%)")
        rc3.metric("Green", f"{result_counts['green']} ({result_counts['green']/ts*100:.0f}%)")

        number_freq = {}
        for r in st.session_state.session_log:
            num = r["result"]
            number_freq[num] = number_freq.get(num, 0) + 1

        if ts >= 5:
            hot = sorted(number_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            cold_all = [str(n) for n in (list(range(0, 37)) + (["00"] if variant_key == "American" else [])) if str(n) not in number_freq and get_display(n) not in number_freq]
            st.markdown(f"**Hot numbers:** {', '.join(f'{n} ({c}x)' for n, c in hot)}")
            if cold_all:
                st.markdown(f"**Cold numbers (never hit):** {', '.join(cold_all[:10])}")
            st.caption("Remember: each spin is independent. Hot/cold numbers are a common fallacy — past results don't influence future spins!")

if not st.session_state.bets and not st.session_state.session_log:
    st.info("Select numbers from the dropdown or tap outside bets, then hit SPIN!")

    with st.expander("Roulette Odds Reference", expanded=True):
        st.dataframe(pd.DataFrame({
            "Bet": ["Straight (1 number)", "Red / Black", "Odd / Even", "1-18 / 19-36", "Dozen (12 numbers)", "Column (12 numbers)"],
            "Payout": ["35:1", "1:1", "1:1", "1:1", "2:1", "2:1"],
            "Win % (EUR)": ["2.70%", "48.65%", "48.65%", "48.65%", "32.43%", "32.43%"],
            "Win % (USA)": ["2.63%", "47.37%", "47.37%", "47.37%", "31.58%", "31.58%"],
            "House Edge (EUR)": ["2.70%", "2.70%", "2.70%", "2.70%", "2.70%", "2.70%"],
            "House Edge (USA)": ["5.26%", "5.26%", "5.26%", "5.26%", "5.26%", "5.26%"],
        }), use_container_width=True, hide_index=True)

        st.markdown("""
**Quick Probability Primer:**
- **House edge** = the percentage of each bet the casino keeps on average. It comes from the zero pocket(s) — they pay out as if zeros don't exist, but they do.
- **European vs American**: One zero (2.70% edge) vs two zeros (5.26% edge). Always prefer European if available.
- **Variance vs Edge**: You can win in the short term (variance), but the house edge is mathematically guaranteed to win over thousands of spins.
- **Independent events**: The wheel has no memory. A streak of 10 reds does NOT make black more likely.
""")
