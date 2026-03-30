import streamlit as st
import secrets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(page_title="Roulette Simulator", page_icon="\U0001F3B0", layout="wide")

RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

BOARD_LAYOUT = [
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

def get_bg_color(n):
    if n == 0 or n == -1:
        return "#2E7D32"
    if n in RED_NUMBERS:
        return "#C62828"
    return "#212121"

def spin_wheel(variant):
    if variant == "American":
        pockets = list(range(0, 37)) + [-1]
    else:
        pockets = list(range(0, 37))
    return secrets.choice(pockets)

def evaluate_bet(bet_type, bet_numbers, result, variant):
    total = 38 if variant == "American" else 37
    win = result in bet_numbers
    payout_map = {
        "straight": 35, "split": 17, "street": 11, "corner": 8,
        "six_line": 5, "dozen": 2, "column": 2,
        "red": 1, "black": 1, "odd": 1, "even": 1, "low": 1, "high": 1,
    }
    payout = payout_map.get(bet_type, 0)
    win_n = len(bet_numbers)
    pw = win_n / total
    he = 1 - (pw * (payout + 1))
    return win, payout, pw, 1 - pw, he, win_n, total

def get_bet_numbers(bet_type, bet_value, variant):
    numbers = []
    if bet_type == "straight":
        numbers = [bet_value]
    elif bet_type == "red":
        numbers = list(RED_NUMBERS)
    elif bet_type == "black":
        numbers = list(BLACK_NUMBERS)
    elif bet_type == "odd":
        numbers = [n for n in range(1, 37) if n % 2 == 1]
    elif bet_type == "even":
        numbers = [n for n in range(1, 37) if n % 2 == 0]
    elif bet_type == "low":
        numbers = list(range(1, 19))
    elif bet_type == "high":
        numbers = list(range(19, 37))
    elif bet_type == "dozen":
        if bet_value == 1:
            numbers = list(range(1, 13))
        elif bet_value == 2:
            numbers = list(range(13, 25))
        else:
            numbers = list(range(25, 37))
    elif bet_type == "column":
        if bet_value == 1:
            numbers = [n for n in range(1, 37) if n % 3 == 1]
        elif bet_value == 2:
            numbers = [n for n in range(1, 37) if n % 3 == 2]
        else:
            numbers = [n for n in range(1, 37) if n % 3 == 0]
    return numbers

if "bets" not in st.session_state:
    st.session_state.bets = []
if "balance" not in st.session_state:
    st.session_state.balance = 1000
if "session_log" not in st.session_state:
    st.session_state.session_log = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "chip_size" not in st.session_state:
    st.session_state.chip_size = 10

BOARD_CSS = """
<style>
.roulette-table {
    background: #1B5E20;
    border: 3px solid #FFD700;
    border-radius: 12px;
    padding: 15px;
    display: inline-block;
    width: 100%;
    box-sizing: border-box;
}
.roulette-title {
    text-align: center;
    color: #FFD700;
    font-size: 22px;
    font-weight: bold;
    font-family: serif;
    margin-bottom: 5px;
}
.roulette-balance {
    text-align: center;
    color: white;
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
}
.board-grid {
    display: grid;
    grid-template-columns: 60px repeat(12, 1fr) 50px;
    gap: 3px;
    margin-bottom: 8px;
}
.num-cell {
    padding: 10px 4px;
    text-align: center;
    color: white;
    font-weight: bold;
    font-size: 14px;
    border-radius: 5px;
    border: 1px solid #8D6E63;
    cursor: pointer;
    min-height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.num-cell.red { background: #C62828; }
.num-cell.black { background: #212121; }
.num-cell.green { background: #2E7D32; }
.num-cell.brown { background: #5D4037; }
.num-cell.selected { border: 3px solid #FFD700 !important; box-shadow: 0 0 8px #FFD700; }
.num-cell.result-hit { border: 3px solid #FFD700 !important; box-shadow: 0 0 12px #FFD700; position: relative; }
.num-cell.result-hit::after { content: "\u2B50"; position: absolute; top: -5px; right: -5px; font-size: 12px; }
.zero-cell {
    grid-row: 1 / 4;
    grid-column: 1;
    background: #2E7D32;
    color: white;
    font-weight: bold;
    font-size: 18px;
    border-radius: 5px;
    border: 2px solid #FFD700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 10px;
}
.col-bet {
    grid-column: 14;
    background: #5D4037;
    color: white;
    font-weight: bold;
    font-size: 11px;
    border-radius: 5px;
    border: 1px solid #8D6E63;
    display: flex;
    align-items: center;
    justify-content: center;
}
.outside-row {
    display: grid;
    grid-template-columns: 60px repeat(3, 1fr);
    gap: 3px;
    margin-bottom: 4px;
}
.outside-cell {
    padding: 8px;
    text-align: center;
    color: white;
    font-weight: bold;
    font-size: 13px;
    border-radius: 5px;
    border: 1px solid #8D6E63;
}
.even-money-row {
    display: grid;
    grid-template-columns: 60px repeat(6, 1fr);
    gap: 3px;
}
.result-display {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    border: 3px solid #FFD700;
    color: white;
    font-weight: bold;
    font-size: 20px;
    margin: 0 auto;
}
.chip-indicator {
    background: #FFD700;
    color: black;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    font-size: 9px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-top: 2px;
}
</style>
"""

def render_board_html(variant, selected_bets, last_result):
    html = BOARD_CSS
    html += '<div class="roulette-table">'
    title = "American Roulette" if variant == "American" else "European Roulette"
    html += f'<div class="roulette-title">{title}</div>'
    html += f'<div class="roulette-balance">Balance: ${st.session_state.balance:,}</div>'

    if last_result is not None:
        res_bg = get_bg_color(last_result)
        res_label = get_display(last_result)
        html += f'<div style="text-align:center; margin-bottom:10px;">'
        html += f'<span style="color:#FFD700; font-weight:bold; margin-right:8px;">LAST RESULT:</span>'
        html += f'<span class="result-display" style="background:{res_bg};">{res_label}</span>'
        html += '</div>'

    selected_nums = set()
    for b in selected_bets:
        for n in b["numbers"]:
            selected_nums.add(n)

    html += '<div class="board-grid">'

    if variant == "American":
        zero_content = '<div>0</div><div style="border-top:1px solid #FFD700; padding-top:6px;">00</div>'
    else:
        zero_content = '0'
    zero_cls = "zero-cell"
    if 0 in selected_nums:
        zero_cls += " selected"
    if last_result is not None and last_result == 0:
        zero_cls += " result-hit"
    html += f'<div class="{zero_cls}">{zero_content}</div>'

    for row_idx, row in enumerate(BOARD_LAYOUT):
        for col_idx, num in enumerate(row):
            color_cls = "red" if num in RED_NUMBERS else "black"
            extra_cls = ""
            if num in selected_nums:
                extra_cls += " selected"
            if last_result is not None and last_result == num:
                extra_cls += " result-hit"
            style = f"grid-row: {row_idx + 1}; grid-column: {col_idx + 2};"
            html += f'<div class="num-cell {color_cls}{extra_cls}" style="{style}">{num}</div>'

    for row_idx, label in enumerate(["2:1", "2:1", "2:1"]):
        html += f'<div class="col-bet" style="grid-row:{row_idx+1}; grid-column:14;">{label}</div>'

    html += '</div>'

    html += '<div class="outside-row">'
    html += '<div></div>'
    for label in ["1st 12", "2nd 12", "3rd 12"]:
        html += f'<div class="outside-cell brown" style="background:#5D4037;">{label}</div>'
    html += '</div>'

    html += '<div class="even-money-row">'
    html += '<div></div>'
    em_bets = [
        ("1-18", "#5D4037"), ("EVEN", "#5D4037"), ("RED", "#C62828"),
        ("BLACK", "#212121"), ("ODD", "#5D4037"), ("19-36", "#5D4037"),
    ]
    for label, bg in em_bets:
        html += f'<div class="outside-cell" style="background:{bg};">{label}</div>'
    html += '</div></div>'
    return html

st.title("\U0001F3B0 Roulette Simulator")
st.caption("Click the board to place bets, then spin!")

with st.sidebar:
    st.header("\u2699\uFE0F Game Settings")
    variant = st.selectbox("Roulette Variant", ["European (37 pockets)", "American (38 pockets)"])
    variant_key = "American" if "American" in variant else "European"
    st.divider()
    st.subheader("Starting Balance")
    new_balance = st.number_input("Set Balance ($)", min_value=10, max_value=1000000, value=st.session_state.balance, step=100)
    if new_balance != st.session_state.balance and not st.session_state.session_log:
        st.session_state.balance = new_balance
    st.divider()
    st.subheader("\U0001F4B0 Chip Size")
    st.session_state.chip_size = st.select_slider("Bet per click", options=[1, 5, 10, 25, 50, 100, 500], value=st.session_state.chip_size)
    st.divider()
    if st.button("\U0001F504 New Session", use_container_width=True):
        st.session_state.bets = []
        st.session_state.session_log = []
        st.session_state.last_result = None
        st.session_state.balance = 1000
        st.rerun()

board_html = render_board_html(variant_key, st.session_state.bets, st.session_state.last_result)
st.markdown(board_html, unsafe_allow_html=True)

st.markdown("---")
st.subheader("\U0001F3AF Place Your Bets")

bet_col1, bet_col2 = st.columns(2)

with bet_col1:
    st.markdown("**Number Bets (click to place)**")
    zero_cols = st.columns(2) if variant_key == "American" else [st.columns(1)[0]]
    if variant_key == "American":
        with zero_cols[0]:
            if st.button("0", key="btn_0", use_container_width=True):
                st.session_state.bets.append({"type": "straight", "numbers": [0], "label": "0", "amount": st.session_state.chip_size})
                st.rerun()
        with zero_cols[1]:
            if st.button("00", key="btn_00", use_container_width=True):
                st.session_state.bets.append({"type": "straight", "numbers": [-1], "label": "00", "amount": st.session_state.chip_size})
                st.rerun()
    else:
        with zero_cols:
            if st.button("0", key="btn_0", use_container_width=True):
                st.session_state.bets.append({"type": "straight", "numbers": [0], "label": "0", "amount": st.session_state.chip_size})
                st.rerun()

    for row in BOARD_LAYOUT:
        cols = st.columns(12)
        for i, num in enumerate(row):
            bg = "#C62828" if num in RED_NUMBERS else "#333"
            with cols[i]:
                if st.button(str(num), key=f"btn_{num}", use_container_width=True):
                    st.session_state.bets.append({"type": "straight", "numbers": [num], "label": str(num), "amount": st.session_state.chip_size})
                    st.rerun()

with bet_col2:
    st.markdown("**Outside Bets**")
    oc1, oc2, oc3 = st.columns(3)
    with oc1:
        if st.button("\U0001F534 Red", key="bet_red", use_container_width=True):
            st.session_state.bets.append({"type": "red", "numbers": get_bet_numbers("red", None, variant_key), "label": "Red", "amount": st.session_state.chip_size})
            st.rerun()
    with oc2:
        if st.button("\u26AB Black", key="bet_black", use_container_width=True):
            st.session_state.bets.append({"type": "black", "numbers": get_bet_numbers("black", None, variant_key), "label": "Black", "amount": st.session_state.chip_size})
            st.rerun()
    with oc3:
        if st.button("\U0001F7E2 0/00", key="bet_green", use_container_width=True):
            nums = [0, -1] if variant_key == "American" else [0]
            st.session_state.bets.append({"type": "straight", "numbers": nums, "label": "Green", "amount": st.session_state.chip_size})
            st.rerun()

    oc4, oc5 = st.columns(2)
    with oc4:
        if st.button("Odd", key="bet_odd", use_container_width=True):
            st.session_state.bets.append({"type": "odd", "numbers": get_bet_numbers("odd", None, variant_key), "label": "Odd", "amount": st.session_state.chip_size})
            st.rerun()
    with oc5:
        if st.button("Even", key="bet_even", use_container_width=True):
            st.session_state.bets.append({"type": "even", "numbers": get_bet_numbers("even", None, variant_key), "label": "Even", "amount": st.session_state.chip_size})
            st.rerun()

    oc6, oc7 = st.columns(2)
    with oc6:
        if st.button("Low (1-18)", key="bet_low", use_container_width=True):
            st.session_state.bets.append({"type": "low", "numbers": get_bet_numbers("low", None, variant_key), "label": "Low 1-18", "amount": st.session_state.chip_size})
            st.rerun()
    with oc7:
        if st.button("High (19-36)", key="bet_high", use_container_width=True):
            st.session_state.bets.append({"type": "high", "numbers": get_bet_numbers("high", None, variant_key), "label": "High 19-36", "amount": st.session_state.chip_size})
            st.rerun()

    st.markdown("**Dozens**")
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        if st.button("1st 12", key="bet_d1", use_container_width=True):
            st.session_state.bets.append({"type": "dozen", "numbers": get_bet_numbers("dozen", 1, variant_key), "label": "1st 12", "amount": st.session_state.chip_size})
            st.rerun()
    with dc2:
        if st.button("2nd 12", key="bet_d2", use_container_width=True):
            st.session_state.bets.append({"type": "dozen", "numbers": get_bet_numbers("dozen", 2, variant_key), "label": "2nd 12", "amount": st.session_state.chip_size})
            st.rerun()
    with dc3:
        if st.button("3rd 12", key="bet_d3", use_container_width=True):
            st.session_state.bets.append({"type": "dozen", "numbers": get_bet_numbers("dozen", 3, variant_key), "label": "3rd 12", "amount": st.session_state.chip_size})
            st.rerun()

    st.markdown("**Columns**")
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        if st.button("Col 1", key="bet_c1", use_container_width=True):
            st.session_state.bets.append({"type": "column", "numbers": get_bet_numbers("column", 1, variant_key), "label": "Col 1", "amount": st.session_state.chip_size})
            st.rerun()
    with cc2:
        if st.button("Col 2", key="bet_c2", use_container_width=True):
            st.session_state.bets.append({"type": "column", "numbers": get_bet_numbers("column", 2, variant_key), "label": "Col 2", "amount": st.session_state.chip_size})
            st.rerun()
    with cc3:
        if st.button("Col 3", key="bet_c3", use_container_width=True):
            st.session_state.bets.append({"type": "column", "numbers": get_bet_numbers("column", 3, variant_key), "label": "Col 3", "amount": st.session_state.chip_size})
            st.rerun()

if st.session_state.bets:
    st.markdown("---")
    st.subheader("\U0001F3B2 Current Bets")
    total_wagered = sum(b["amount"] for b in st.session_state.bets)
    bet_summary = {}
    for b in st.session_state.bets:
        key = b["label"]
        if key in bet_summary:
            bet_summary[key]["amount"] += b["amount"]
        else:
            bet_summary[key] = {"type": b["type"], "amount": b["amount"], "numbers": b["numbers"]}

    bet_chips_html = '<div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px;">'
    for label, info in bet_summary.items():
        bg = get_bg_color(info["numbers"][0]) if info["type"] == "straight" else "#5D4037"
        bet_chips_html += f'<span style="background:{bg}; color:white; padding:6px 14px; border-radius:20px; font-weight:bold; border:2px solid #FFD700; font-size:13px;">{label} ${info["amount"]}</span>'
    bet_chips_html += '</div>'
    st.markdown(bet_chips_html, unsafe_allow_html=True)

    mc1, mc2, mc3 = st.columns([1, 2, 1])
    with mc1:
        st.metric("Total Wagered", f"${total_wagered:,}")
    with mc2:
        if st.button("\U0001F3A1 SPIN!", use_container_width=True, type="primary"):
            if total_wagered > st.session_state.balance:
                st.error("Insufficient balance!")
            else:
                st.session_state.balance -= total_wagered
                result = spin_wheel(variant_key)
                st.session_state.last_result = result

                total_won = 0
                bet_results = []
                for b in bet_summary.values():
                    win, payout, pw, pl, he, wn, tp = evaluate_bet(b["type"], b["numbers"], result, variant_key)
                    winnings = 0
                    if win:
                        winnings = b["amount"] * payout + b["amount"]
                        total_won += winnings
                    bet_results.append({"type": b["type"], "amount": b["amount"], "won": win, "winnings": winnings, "pw": pw})

                st.session_state.balance += total_won
                net = total_won - total_wagered

                spin_record = {
                    "spin": len(st.session_state.session_log) + 1,
                    "result": get_display(result),
                    "result_num": result,
                    "color": get_color(result),
                    "total_wagered": total_wagered,
                    "total_won": total_won,
                    "net": net,
                    "balance": st.session_state.balance,
                    "bet_results": bet_results,
                }
                st.session_state.session_log.append(spin_record)
                st.session_state.bets = []
                st.rerun()
    with mc3:
        if st.button("\U0001F5D1 Clear Bets", use_container_width=True):
            st.session_state.bets = []
            st.rerun()

if st.session_state.session_log:
    last = st.session_state.session_log[-1]
    st.markdown("---")
    st.subheader("Last Spin Result")

    color_map = {"red": "\U0001F534", "black": "\u26AB", "green": "\U0001F7E2"}
    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        st.markdown(f"### {color_map.get(last['color'], '')} {last['result']} ({last['color'].upper()})")
    with rc2:
        if last["net"] >= 0:
            st.success(f"**WIN!** +${last['total_won']:,}")
        else:
            st.error(f"**LOSS.** -${last['total_wagered']:,}")
    with rc3:
        st.metric("Net P&L", f"${last['net']:+,}")
    with rc4:
        st.metric("Balance", f"${st.session_state.balance:,}")

    if len(st.session_state.session_log) >= 2:
        st.markdown("---")
        st.subheader("Session Charts")

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor("#0e1117")

        ax1 = axes[0]
        ax1.set_facecolor("#16213e")
        spins_x = [0] + [r["spin"] for r in st.session_state.session_log]
        init_bal = st.session_state.session_log[0]["balance"] - st.session_state.session_log[0]["net"]
        balances = [init_bal] + [r["balance"] for r in st.session_state.session_log]
        ax1.plot(spins_x, balances, color="#00d4aa", linewidth=2, marker="o", markersize=4)
        ax1.fill_between(spins_x, balances, alpha=0.15, color="#00d4aa")
        ax1.axhline(y=init_bal, color="gray", linestyle="--", alpha=0.5, label="Starting")
        ax1.set_title("Balance Over Time", color="white", fontsize=13, fontweight="bold", pad=15)
        ax1.set_xlabel("Spin #", color="white")
        ax1.set_ylabel("Balance ($)", color="white")
        ax1.tick_params(colors="white")
        ax1.legend(facecolor="#16213e", edgecolor="white", labelcolor="white")
        for s in ["top", "right"]:
            ax1.spines[s].set_visible(False)
        for s in ["bottom", "left"]:
            ax1.spines[s].set_color("white")

        ax2 = axes[1]
        ax2.set_facecolor("#16213e")
        cumulative = np.cumsum([r["net"] for r in st.session_state.session_log])
        spin_nums = range(1, len(st.session_state.session_log) + 1)
        ax2.fill_between(spin_nums, cumulative, where=(cumulative >= 0), color="#00d4aa", alpha=0.3)
        ax2.fill_between(spin_nums, cumulative, where=(cumulative < 0), color="#ff4757", alpha=0.3)
        ax2.plot(spin_nums, cumulative, color="white", linewidth=1.5)
        ax2.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")
        ax2.set_title("Cumulative P&L", color="white", fontsize=13, fontweight="bold", pad=15)
        ax2.set_xlabel("Spin #", color="white")
        ax2.set_ylabel("Cumulative P&L ($)", color="white")
        ax2.tick_params(colors="white")
        for s in ["top", "right"]:
            ax2.spines[s].set_visible(False)
        for s in ["bottom", "left"]:
            ax2.spines[s].set_color("white")

        plt.tight_layout()
        st.pyplot(fig)

    with st.expander("View Session Log"):
        log_data = []
        for r in st.session_state.session_log:
            log_data.append({
                "Spin": r["spin"],
                "Result": r["result"],
                "Color": r["color"].upper(),
                "Wagered": f"${r['total_wagered']:,}",
                "Won": f"${r['total_won']:,}",
                "Net": f"${r['net']:+,}",
                "Balance": f"${r['balance']:,}",
            })
        st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)

    total_spins = len(st.session_state.session_log)
    total_won_spins = sum(1 for r in st.session_state.session_log if r["net"] > 0)
    total_net = sum(r["net"] for r in st.session_state.session_log)
    st.markdown("---")
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Total Spins", total_spins)
    sc2.metric("Wins", total_won_spins)
    sc3.metric("Win Rate", f"{total_won_spins/total_spins*100:.1f}%")
    sc4.metric("Session P&L", f"${total_net:+,}")

if not st.session_state.bets and not st.session_state.session_log:
    st.markdown("---")
    st.info("Click numbers on the board above or use the outside bet buttons to place bets, then hit **SPIN!**")
    st.markdown("""
### How it works
- **European Roulette**: 37 pockets (0-36), house edge **2.70%**
- **American Roulette**: 38 pockets (0, 00, 1-36), house edge **5.26%**
- Uses Python `secrets` module for cryptographically secure randomness
- No memory between spins - each spin is independent
- Click multiple numbers to place multiple straight bets
- Use outside bets (Red/Black, Odd/Even, etc.) for better odds
    """)
    bet_info = pd.DataFrame({
        "Bet": ["Straight", "Red/Black", "Even/Odd", "High/Low", "Dozen", "Column"],
        "Payout": ["35:1", "1:1", "1:1", "1:1", "2:1", "2:1"],
        "P(Win) EUR": ["2.70%", "48.65%", "48.65%", "48.65%", "32.43%", "32.43%"],
        "P(Win) USA": ["2.63%", "47.37%", "47.37%", "47.37%", "31.58%", "31.58%"],
    })
    st.dataframe(bet_info, use_container_width=True, hide_index=True)
