import streamlit as st
import secrets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
    height: 48px;
    font-weight: bold;
    font-size: 16px;
    border-radius: 6px;
    transition: all 0.15s;
    padding: 4px 2px;
    min-width: 40px;
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

if variant_key == "American":
    zc1, zc2 = st.columns(2)
    with zc1:
        if st.button("0", key="b_0", use_container_width=True, type="secondary"):
            place_bet("straight", [0], "0")
            st.rerun()
    with zc2:
        if st.button("00", key="b_00", use_container_width=True, type="secondary"):
            place_bet("straight", [-1], "00")
            st.rerun()
else:
    if st.button("0", key="b_0", use_container_width=True, type="secondary"):
        place_bet("straight", [0], "0")
        st.rerun()

for num in [0, -1]:
    bg, hover, border, shadow, hit = btn_style(num)
    safe_key = "b_0" if num == 0 else "b_00"
    st.markdown(f"""<style>
    div[data-testid="stButton"]:has(button[data-testid="stBaseButton-secondary"][kind="secondary"]:has(p:first-child)) button[key="{safe_key}"] {{
        background: {bg}; color: white; border: {border}; box-shadow: {shadow}; {hit}
    }}
    </style>""", unsafe_allow_html=True)

for row_idx, row_nums in enumerate(BOARD_ROWS):
    half1 = row_nums[:6]
    half2 = row_nums[6:]

    cols1 = st.columns(6)
    for i, num in enumerate(half1):
        bg, hover, border, shadow, hit = btn_style(num)
        with cols1[i]:
            st.markdown(f"""<style>
            [data-testid="stButton"] button[kind="secondary"]:has(p) {{
                font-size: 15px;
            }}
            div:has(> [data-testid="stButton"] button[key="b_{num}"]) button {{
                background: {bg} !important;
                color: white !important;
                border: {border} !important;
                box-shadow: {shadow} !important;
                {hit}
            }}
            div:has(> [data-testid="stButton"] button[key="b_{num}"]) button:hover {{
                background: {hover} !important;
                transform: scale(1.08);
            }}
            </style>""", unsafe_allow_html=True)
            if st.button(str(num), key=f"b_{num}", use_container_width=True, type="secondary"):
                place_bet("straight", [num], str(num))
                st.rerun()

    cols2 = st.columns(6)
    for i, num in enumerate(half2):
        bg, hover, border, shadow, hit = btn_style(num)
        with cols2[i]:
            st.markdown(f"""<style>
            div:has(> [data-testid="stButton"] button[key="b_{num}"]) button {{
                background: {bg} !important;
                color: white !important;
                border: {border} !important;
                box-shadow: {shadow} !important;
                {hit}
            }}
            div:has(> [data-testid="stButton"] button[key="b_{num}"]) button:hover {{
                background: {hover} !important;
                transform: scale(1.08);
            }}
            </style>""", unsafe_allow_html=True)
            if st.button(str(num), key=f"b_{num}", use_container_width=True, type="secondary"):
                place_bet("straight", [num], str(num))
                st.rerun()

st.markdown("---")
st.markdown("<p style='color:#FFD700; font-weight:bold; text-align:center; margin:4px 0;'>OUTSIDE BETS</p>",
            unsafe_allow_html=True)

oc1, oc2, oc3 = st.columns(3)
with oc1:
    st.markdown("""<style>
    div:has(> [data-testid="stButton"] button[key="bet_red"]) button {
        background: #C62828 !important; color: white !important; border: 1px solid #FFD700 !important;
    }
    </style>""", unsafe_allow_html=True)
    if st.button("Red", key="bet_red", use_container_width=True, type="secondary"):
        place_bet("red", get_bet_numbers("red", None, variant_key), "Red")
        st.rerun()
with oc2:
    st.markdown("""<style>
    div:has(> [data-testid="stButton"] button[key="bet_black"]) button {
        background: #212121 !important; color: white !important; border: 1px solid #FFD700 !important;
    }
    </style>""", unsafe_allow_html=True)
    if st.button("Black", key="bet_black", use_container_width=True, type="secondary"):
        place_bet("black", get_bet_numbers("black", None, variant_key), "Black")
        st.rerun()
with oc3:
    st.markdown("""<style>
    div:has(> [data-testid="stButton"] button[key="bet_green"]) button {
        background: #2E7D32 !important; color: white !important; border: 1px solid #FFD700 !important;
    }
    </style>""", unsafe_allow_html=True)
    if st.button("0/00", key="bet_green", use_container_width=True, type="secondary"):
        nums = [0, -1] if variant_key == "American" else [0]
        place_bet("straight", nums, "Green")
        st.rerun()

oc4, oc5, oc6, oc7 = st.columns(4)
outside_style = "background: #5D4037 !important; color: white !important; border: 1px solid #8D6E63 !important;"
for col, key, label, btype, bval in [
    (oc4, "bet_odd", "Odd", "odd", None), (oc5, "bet_even", "Even", "even", None),
    (oc6, "bet_low", "1-18", "low", None), (oc7, "bet_high", "19-36", "high", None),
]:
    with col:
        st.markdown(f'<style>div:has(> [data-testid="stButton"] button[key="{key}"]) button {{ {outside_style} }}</style>',
                    unsafe_allow_html=True)
        if st.button(label, key=key, use_container_width=True, type="secondary"):
            place_bet(btype, get_bet_numbers(btype, bval, variant_key), label)
            st.rerun()

dc1, dc2, dc3 = st.columns(3)
for col, key, label, val in [(dc1, "bet_d1", "1st 12", 1), (dc2, "bet_d2", "2nd 12", 2), (dc3, "bet_d3", "3rd 12", 3)]:
    with col:
        st.markdown(f'<style>div:has(> [data-testid="stButton"] button[key="{key}"]) button {{ {outside_style} }}</style>',
                    unsafe_allow_html=True)
        if st.button(label, key=key, use_container_width=True, type="secondary"):
            place_bet("dozen", get_bet_numbers("dozen", val, variant_key), label)
            st.rerun()

cc1, cc2, cc3 = st.columns(3)
for col, key, label, val in [(cc1, "bet_c1", "Col 1", 1), (cc2, "bet_c2", "Col 2", 2), (cc3, "bet_c3", "Col 3", 3)]:
    with col:
        st.markdown(f'<style>div:has(> [data-testid="stButton"] button[key="{key}"]) button {{ {outside_style} }}</style>',
                    unsafe_allow_html=True)
        if st.button(label, key=key, use_container_width=True, type="secondary"):
            place_bet("column", get_bet_numbers("column", val, variant_key), label)
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.bets:
    st.markdown("---")
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
                for b in bet_summary.values():
                    win, payout, pw = evaluate_bet(b["type"], b["numbers"], result, variant_key)
                    if win:
                        total_won += b["amount"] * payout + b["amount"]
                st.session_state.balance += total_won
                net = total_won - total_wagered
                st.session_state.session_log.append({
                    "spin": len(st.session_state.session_log) + 1,
                    "result": get_display(result), "result_num": result,
                    "color": get_color(result), "total_wagered": total_wagered,
                    "total_won": total_won, "net": net,
                    "balance": st.session_state.balance,
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

    with st.expander("Session Log"):
        st.dataframe(pd.DataFrame([{
            "Spin": r["spin"], "Result": r["result"], "Color": r["color"].upper(),
            "Wagered": f"${r['total_wagered']:,}", "Won": f"${r['total_won']:,}",
            "Net": f"${r['net']:+,}", "Balance": f"${r['balance']:,}",
        } for r in st.session_state.session_log]), use_container_width=True, hide_index=True)

    ts = len(st.session_state.session_log)
    tw = sum(1 for r in st.session_state.session_log if r["net"] > 0)
    tn = sum(r["net"] for r in st.session_state.session_log)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Spins", ts)
    m2.metric("Wins", tw)
    m3.metric("Win %", f"{tw/ts*100:.0f}%")
    m4.metric("P&L", f"${tn:+,}")

if not st.session_state.bets and not st.session_state.session_log:
    st.info("Tap any number on the board to place a bet, then hit SPIN!")
    st.dataframe(pd.DataFrame({
        "Bet": ["Straight", "Red/Black", "Odd/Even", "1-18/19-36", "Dozen", "Column"],
        "Payout": ["35:1", "1:1", "1:1", "1:1", "2:1", "2:1"],
        "Win % (EUR)": ["2.7%", "48.6%", "48.6%", "48.6%", "32.4%", "32.4%"],
        "Win % (USA)": ["2.6%", "47.4%", "47.4%", "47.4%", "31.6%", "31.6%"],
    }), use_container_width=True, hide_index=True)
