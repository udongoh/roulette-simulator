import streamlit as st
import secrets
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Roulette Simulator", page_icon="\U0001F3B0", layout="wide")
st.title("\U0001F3B0 Roulette Simulator")
st.caption("Realistic probability engine using cryptographic randomness | No memory between spins")

RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

def spin_wheel(variant):
    if variant == "American":
        pockets = list(range(0, 37)) + [-1]
    else:
        pockets = list(range(0, 37))
    return secrets.choice(pockets)

def get_color(n):
    if n == 0 or n == -1:
        return "green"
    return "red" if n in RED_NUMBERS else "black"

def get_display(n):
    return "00" if n == -1 else str(n)

def evaluate(bet_type, bet_value, result, variant):
    total = 38 if variant == "American" else 37
    if bet_type == "Straight (single number)":
        win = (result == bet_value)
        payout, win_n = 35, 1
    elif bet_type == "Red / Black":
        target = RED_NUMBERS if bet_value == "Red" else BLACK_NUMBERS
        win = (result in target)
        payout, win_n = 1, 18
    elif bet_type == "Even / Odd":
        if result <= 0:
            win = False
        elif bet_value == "Even":
            win = (result % 2 == 0)
        else:
            win = (result % 2 == 1)
        payout, win_n = 1, 18
    elif bet_type == "High / Low":
        if result <= 0:
            win = False
        elif bet_value == "Low (1-18)":
            win = (1 <= result <= 18)
        else:
            win = (19 <= result <= 36)
        payout, win_n = 1, 18
    elif bet_type == "Dozen":
        d = int(bet_value[0])
        if d == 1:
            win = (1 <= result <= 12)
        elif d == 2:
            win = (13 <= result <= 24)
        else:
            win = (25 <= result <= 36)
        payout, win_n = 2, 12
    elif bet_type == "Column":
        col = int(bet_value.split(" ")[1])
        if result <= 0:
            win = False
        elif col == 3:
            win = (result % 3 == 0)
        else:
            win = (result % 3 == col)
        payout, win_n = 2, 12
    else:
        win, payout, win_n = False, 0, 0
    pw = win_n / total
    he = 1 - (pw * (payout + 1))
    return win, payout, pw, 1 - pw, he, win_n, total

with st.sidebar:
    st.header("\u2699\uFE0F Game Settings")
    variant = st.selectbox("Roulette Variant", ["European (37 pockets)", "American (38 pockets)"])
    variant_key = "American" if "American" in variant else "European"
    st.divider()
    bet_amount = st.slider("Bet Amount ($)", min_value=1, max_value=10000, value=100, step=1)
    st.divider()
    bet_type = st.selectbox("Bet Type", [
        "Red / Black", "Even / Odd", "High / Low",
        "Dozen", "Column", "Straight (single number)"
    ])
    if bet_type == "Red / Black":
        bet_value = st.radio("Pick", ["Red", "Black"], horizontal=True)
    elif bet_type == "Even / Odd":
        bet_value = st.radio("Pick", ["Even", "Odd"], horizontal=True)
    elif bet_type == "High / Low":
        bet_value = st.radio("Pick", ["Low (1-18)", "High (19-36)"], horizontal=True)
    elif bet_type == "Dozen":
        bet_value = st.radio("Pick", ["1st (1-12)", "2nd (13-24)", "3rd (25-36)"], horizontal=True)
    elif bet_type == "Column":
        bet_value = st.radio("Pick", ["Col 1", "Col 2", "Col 3"], horizontal=True)
    elif bet_type == "Straight (single number)":
        bet_value = st.number_input("Pick Number (0-36)", min_value=0, max_value=36, value=17)
    st.divider()
    num_spins = st.slider("Number of Spins", min_value=1, max_value=500, value=1)
    st.divider()
    spin_button = st.button("\U0001F3A1 SPIN!", use_container_width=True, type="primary")

if spin_button:
    results = []
    for i in range(num_spins):
        number = spin_wheel(variant_key)
        win, payout, pw, pl, he, wn, tp = evaluate(bet_type, bet_value, number, variant_key)
        net = bet_amount * payout if win else -bet_amount
        results.append({"spin": i + 1, "number": get_display(number), "color": get_color(number),
                        "win": win, "net": net, "payout": payout})

    pw_pct = pw * 100
    pl_pct = pl * 100
    total_wagered = bet_amount * num_spins
    total_net = sum(r["net"] for r in results)
    wins = sum(1 for r in results if r["win"])
    losses = num_spins - wins

    if num_spins == 1:
        r = results[0]
        color_map = {"red": "\U0001F534", "black": "\u26AB", "green": "\U0001F7E2"}
        col_res, col_prob = st.columns([1, 1])
        with col_res:
            st.subheader("Result")
            st.markdown("### " + color_map[r["color"]] + " " + r["number"] + " (" + r["color"].upper() + ")")
            if r["win"]:
                st.success("**WIN!** You won ${:,.0f}".format(bet_amount * payout))
            else:
                st.error("**LOSS.** You lost ${:,.0f}".format(bet_amount))
            st.metric("Net P&L", "${:+,.0f}".format(r["net"]))
        with col_prob:
            st.subheader("Probability Analysis")
            st.metric("P(Win)", "{:.2f}%".format(pw_pct))
            st.metric("P(Lose)", "{:.2f}%".format(pl_pct))
            st.metric("House Edge", "{:.2f}%".format(he * 100))
            st.metric("Payout Ratio", str(payout) + ":1")
            st.caption(str(wn) + " winning outcomes out of " + str(tp) + " pockets")
    else:
        st.subheader("Session Results - " + str(num_spins) + " Spins")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Wins", str(wins))
        c2.metric("Losses", str(losses))
        c3.metric("Win Rate", "{:.1f}%".format(wins / num_spins * 100))
        c4.metric("Total Wagered", "${:,.0f}".format(total_wagered))
        c5.metric("Net P&L", "${:+,.0f}".format(total_net))

    st.divider()

    fig, axes = plt.subplots(1, 3 if num_spins > 1 else 2, figsize=(16 if num_spins > 1 else 11, 5))
    fig.patch.set_facecolor("#0e1117")

    ax1 = axes[0]
    sizes = [pw_pct, pl_pct]
    colors_chart = ["#00d4aa", "#ff4757"]
    labels = ["Win {:.2f}%".format(pw_pct), "Lose {:.2f}%".format(pl_pct)]
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors_chart, autopct="%.1f%%",
        startangle=90, pctdistance=0.75, textprops={"color": "white", "fontsize": 11})
    ax1.add_artist(plt.Circle((0, 0), 0.55, fc="#0e1117"))
    ax1.set_title("Win/Lose Probability", color="white", fontsize=13, fontweight="bold", pad=15)

    ax2 = axes[1]
    ax2.set_facecolor("#16213e")
    val_win = bet_amount * payout
    val_lose = -bet_amount
    bars = ax2.bar(["If Win", "If Lose"], [val_win, val_lose],
        color=["#00d4aa", "#ff4757"], width=0.5, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, [val_win, val_lose]):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + (10 if val > 0 else -15),
            "${:+,.0f}".format(val), ha="center", color="white", fontsize=13, fontweight="bold")
    ax2.set_title("Payout Structure", color="white", fontsize=13, fontweight="bold", pad=15)
    ax2.set_ylabel("Amount ($)", color="white")
    ax2.axhline(y=0, color="white", linewidth=0.5)
    ax2.tick_params(colors="white")
    for s in ["top", "right"]:
        ax2.spines[s].set_visible(False)
    for s in ["bottom", "left"]:
        ax2.spines[s].set_color("white")

    if num_spins > 1:
        ax3 = axes[2]
        ax3.set_facecolor("#16213e")
        cumulative = np.cumsum([r["net"] for r in results])
        spins = range(1, num_spins + 1)
        ax3.fill_between(spins, cumulative, where=(cumulative >= 0), color="#00d4aa", alpha=0.3)
        ax3.fill_between(spins, cumulative, where=(cumulative < 0), color="#ff4757", alpha=0.3)
        ax3.plot(spins, cumulative, color="white", linewidth=1.5)
        ax3.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")
        ev_line = [-he * bet_amount * i for i in spins]
        ax3.plot(spins, ev_line, color="#ffa502", linewidth=1, linestyle="--", label="Expected Value")
        ax3.set_title("Cumulative P&L", color="white", fontsize=13, fontweight="bold", pad=15)
        ax3.set_xlabel("Spin #", color="white")
        ax3.set_ylabel("Cumulative P&L ($)", color="white")
        ax3.tick_params(colors="white")
        for s in ["top", "right"]:
            ax3.spines[s].set_visible(False)
        for s in ["bottom", "left"]:
            ax3.spines[s].set_color("white")
        ax3.legend(facecolor="#16213e", edgecolor="white", labelcolor="white")

    plt.tight_layout()
    st.pyplot(fig)

    if num_spins > 1:
        st.divider()
        import pandas as pd
        with st.expander("View Spin Log"):
            log_df = pd.DataFrame(results)
            log_df.columns = ["Spin", "Number", "Color", "Win", "Net ($)", "Payout"]
            log_df["Win"] = log_df["Win"].map({True: "Yes", False: "No"})
            st.dataframe(log_df.drop(columns=["Payout"]), use_container_width=True, height=400)

        st.subheader("Probability vs Actual")
        p1, p2, p3 = st.columns(3)
        p1.metric("Expected Win Rate", "{:.2f}%".format(pw_pct))
        p2.metric("Actual Win Rate", "{:.1f}%".format(wins / num_spins * 100),
            delta="{:+.1f}%".format(wins / num_spins * 100 - pw_pct))
        ev_session = -he * total_wagered
        p3.metric("Expected Loss", "${:,.0f}".format(abs(ev_session)),
            delta="${:+,.0f} vs actual".format(total_net - ev_session))

else:
    st.info("Configure your bet in the sidebar and click **SPIN!** to play.")
    st.markdown("### How it works")
    st.markdown("""
- **European Roulette**: 37 pockets (0-36), house edge **2.70%**
- **American Roulette**: 38 pockets (0, 00, 1-36), house edge **5.26%**
- Uses Python `secrets` module for cryptographically secure randomness
- No memory between spins - each run is independent
    """)
    import pandas as pd
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Bet Types & Payouts")
        bets = pd.DataFrame({
            "Bet": ["Red/Black", "Even/Odd", "High/Low", "Dozen", "Column", "Straight"],
            "Payout": ["1:1", "1:1", "1:1", "2:1", "2:1", "35:1"],
            "P(Win) EUR": ["48.65%", "48.65%", "48.65%", "32.43%", "32.43%", "2.70%"],
            "P(Win) USA": ["47.37%", "47.37%", "47.37%", "31.58%", "31.58%", "2.63%"]
        })
        st.dataframe(bets, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("#### House Edge Explained")
        st.markdown("""
The house edge comes from the **green zero pocket(s)**:
- A fair 1:1 bet on Red covers 18/37 pockets = 48.65% (not 50%)
- Over time, the house keeps ~2.70% (EUR) or ~5.26% (USA) of all bets
- **No strategy can overcome the house edge** in the long run
        """)
