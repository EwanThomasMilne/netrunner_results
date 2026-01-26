# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.3
#   kernelspec:
#     display_name: .venv (3.13.5)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Overview of Results
#
# Do some analysis on results, assume `kikai` / `not_yeti` have done the hardwork and properly normalised names etc.
#
# ## Using Notebook
#
# Ensure prerequisites:
#
# ```shell
# pip install -r src/visualisations/extra-requirements.txt
# ```

# %%
# Update results etc, remember to update tournaments.yml for what you care about
import os
import subprocess
import sys
from pathlib import Path

env = dict(os.environ)
env["PYTHONUNBUFFERED"] = "1"

proc = subprocess.Popen(
    [sys.executable, "-u", Path("src", "netrunner_results.py")],  # Use same kernel
    cwd=Path("..", ".."),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

try:
    for line in proc.stdout:
        print(line, end="")
finally:
    if proc.stdout:
        proc.stdout.close()
    rc = proc.wait()

# %%
# Data load and utilities
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

faction_colors = {
    "Anarch": "#e21b3c",
    "Criminal": "#0011ff",
    "Shaper": "#2ca02c",
    "HB": "#9467bd",
    "Jinteki": "#e21b3c",
    "Weyland": "#2ca02c",
    "NBN": "#fbff0e",
    "Mini-faction": "#7f7f7f",
    "Neutral Corp": "#7f7f7f",
    "Neutral Runner": "#7f7f7f",
}

LOW_GAME_CUTOFF_P = 0.035

BASE_DIR = Path("..", "..")
DATA_DIR = Path(BASE_DIR, "OUTPUT")
RESULTS_DIR = Path(DATA_DIR, "results")
STANDINGS_DIR = Path(DATA_DIR, "standings")


### Identities
with open(Path(BASE_DIR, "src", "netrunner", "identities.yml"), "r", encoding="utf-8") as f:
    identities = yaml.safe_load(f)

id_to_faction = {}
for name, data in identities.items():
    faction = data.get("faction")
    id_to_faction[name] = faction
    for alt in data.get("alt_names", []) or []:
        id_to_faction[alt] = faction

valid_identities = set(id_to_faction.keys())

### Standings
standing_frames = []
FILES = sorted(STANDINGS_DIR.rglob("*.csv"))
for fp in FILES:
    df = pd.read_csv(
        fp,
        header=0,
        parse_dates=["date"],
        # keep_default_na=False,
        encoding="utf-8",
        engine="python",
    )

    standing_frames.append(df)

standings = pd.concat(standing_frames, ignore_index=True)

### Match results
res_frames = []
FILES = sorted(RESULTS_DIR.rglob("*.csv"))
for fp in FILES:
    df = pd.read_csv(
        fp,
        header=0,
        parse_dates=["date"],
        # keep_default_na=False,
        encoding="utf-8",
        engine="python",
    )

    res_frames.append(df)

results = pd.concat(res_frames, ignore_index=True)
results_unfiltered = results.copy()

### Label byes
mask_invalid = ~results["corp_id"].isin(valid_identities) | ~results["runner_id"].isin(valid_identities)
results.loc[mask_invalid, "result"] = "bye"

### Remove all byes and IDs
mask_byes_ids = results["result"].isin(["bye", "ID"])
results = results[~mask_byes_ids]

### Get player-tournament win rates
res_data_ext = results.copy()

corp_rows = res_data_ext.rename(columns={"corp_player": "player"})[
    ["player", "tournament", "tournament_id", "phase", "result"]
].assign(side="corp", win=lambda x: x["result"].eq("corp"))

runner_rows = res_data_ext.rename(columns={"runner_player": "player"})[
    ["player", "tournament", "tournament_id", "phase", "result"]
].assign(side="runner", win=lambda x: x["result"].eq("runner"))

res_data_ext = pd.concat([corp_rows, runner_rows], ignore_index=True)
res_data_ext = res_data_ext[res_data_ext["phase"].isin(["swiss", "cut"])]  # Just in case

grp = (
    res_data_ext.groupby(["player", "tournament", "side", "phase"], dropna=True)
    .agg(games=("win", "size"), wins=("win", "sum"))
    .reset_index()
)
grp["winrate"] = grp["wins"] / grp["games"]

# pivot swiss/cut
wide_sc = grp.pivot_table(index=["player", "tournament"], columns=["side", "phase"], values="winrate")

grp_side_overall = (
    res_data_ext.groupby(["player", "tournament", "side"], dropna=True)
    .agg(games=("win", "size"), wins=("win", "sum"))
    .reset_index()
)
grp_side_overall["winrate"] = grp_side_overall["wins"] / grp_side_overall["games"]

wide_side_overall = grp_side_overall.pivot_table(index=["player", "tournament"], columns=["side"], values="winrate")
wide_side_overall.columns = pd.MultiIndex.from_product([wide_side_overall.columns, ["overall"]])

grp_all_overall = res_data_ext.groupby(["player", "tournament"], dropna=False).agg(
    games=("win", "size"), wins=("win", "sum")
)
grp_all_overall["winrate"] = grp_all_overall["wins"] / grp_all_overall["games"]
wide_all_overall = grp_all_overall[["winrate"]].rename(columns={"winrate": ("all", "overall")})
wide_all_overall.columns = pd.MultiIndex.from_tuples(wide_all_overall.columns)

player_wr_df = pd.concat([wide_sc, wide_side_overall, wide_all_overall], axis=1)

desired_cols = [
    ("corp", "swiss"),
    ("corp", "cut"),
    ("corp", "overall"),
    ("runner", "swiss"),
    ("runner", "cut"),
    ("runner", "overall"),
    ("all", "overall"),
]
existing = [c for c in desired_cols if c in player_wr_df.columns]
rest = [c for c in player_wr_df.columns if c not in existing]
player_wr_df = player_wr_df[existing + rest]

player_wr_df.sort_index()

LOSER_SIDE_MIN_WR = 0.1
games = results.copy()
corp_overall_wr = player_wr_df[("corp", "overall")].rename("corp_overall_wr")
runner_overall_wr = player_wr_df[("runner", "overall")].rename("runner_overall_wr")
games = games.merge(
    corp_overall_wr.reset_index(),
    left_on=["corp_player", "tournament"],
    right_on=["player", "tournament"],
    how="left",
)
games = games.drop(columns=["player"])
games = games.merge(
    runner_overall_wr.reset_index(),
    left_on=["runner_player", "tournament"],
    right_on=["player", "tournament"],
    how="left",
)
games = games.drop(columns=["player"])

loser_low_wr = ((games["result"] == "corp") & (games["runner_overall_wr"].fillna(0) < LOSER_SIDE_MIN_WR)) | (
    (games["result"] == "runner") & (games["corp_overall_wr"].fillna(0) < LOSER_SIDE_MIN_WR)
)

results = games.loc[~loser_low_wr].copy()

### Summarise
tournaments = results["tournament"].dropna().unique()

print(f"Number of tournaments: {len(FILES)}")
for t in sorted(tournaments):
    print(" -", t)
print(f"Number of games: {len(results)}")
print(f"  Removed {sum(mask_byes_ids)} byes and IDs")
print(f"  Removed {loser_low_wr.sum()} games where loser winrate was below {LOSER_SIDE_MIN_WR*100:.1f}%")

# %% [markdown]
# ## Follow Pro Players
#
# Cut data to follow only the best players for some definition of "best"

# %%
import re
from typing import Any

import numpy as np
import pandas as pd
from bokeh.io import output_file, output_notebook, save
from bokeh.layouts import column, row
from bokeh.models import (
    ColumnDataSource,
    CustomJS,
    Div,
    HoverTool,
    NumeralTickFormatter,
    RadioButtonGroup,
)
from bokeh.plotting import figure, show

output_notebook()


def _apply_low_game_flags(df: pd.DataFrame, cutoff: int) -> pd.DataFrame:
    d = df.copy()
    d["is_low"] = d["games"] < cutoff
    d["alpha"] = np.where(d["is_low"], 0.35, 1.0)  # For fading on graph
    d["winrate_pct"] = (d["winrate"] * 100).round(2)
    d["low_label"] = np.where(d["is_low"], "<b>(LOW)</b>", "")  # Label for tooltip
    return d


def _abbrev_list(items, max_items=7, max_chars=400):
    """Join unique with <br>, trim length, and add '+N more' if overflowing"""
    uniq = list(dict.fromkeys(items))
    shown = uniq[:max_items]
    s = "<br>".join(shown)
    truncated = False
    if len(s) > max_chars:
        s = s[: max_chars - 1].rstrip() + ".."
        truncated = True
    more = max(0, len(uniq) - len(shown))
    if more or truncated:
        s += f"<br><em>+{more} more..</em>" if more else "<br><em>..</em>"
    return s


def _agg_identity_winrate(df: pd.DataFrame, who: str) -> pd.DataFrame:
    d = df.copy()
    d["result"] = d["result"].astype(str).str.lower()

    id_col = f"{who}_id"
    faction_col = f"{who}_faction"
    flag_col = f"{who}_is_tracked"
    player_col = (
        f"{who}_player" if f"{who}_player" in d.columns else ("corp_player" if who == "corp" else "runner_player")
    )

    # Keep only rows where the relevant side was playing
    d = d[d[flag_col]]

    # Add sample label
    d["sample_pair"] = d[player_col].astype(str).str.strip() + " - " + d["tournament"].astype(str)

    grp = d.groupby([id_col, faction_col], dropna=False, as_index=False).agg(
        games=("result", "size"),
        wins=("result", lambda s: (s == who).sum()),
        pairs=("sample_pair", lambda s: _abbrev_list(s)),
    )

    grp["winrate"] = grp["wins"] / grp["games"]
    grp.rename(columns={id_col: "identity", faction_col: "faction", "pairs": "examples"}, inplace=True)
    return grp.sort_values(["winrate", "games"], ascending=[False, False])


def _top_n(df: pd.DataFrame, n: int = 30) -> pd.DataFrame:
    top_by_games = df.sort_values(["games", "winrate"], ascending=[False, False]).head(n).copy()
    top_by_games.sort_values(["winrate", "games", "identity"], ascending=[False, False, True], inplace=True)
    return top_by_games


def _build_flags_for_split(split_key: str) -> tuple[pd.DataFrame, list[Any], list[str]]:
    cutters = standings.copy()
    cutters["top_cut_rank_num"] = pd.to_numeric(cutters["top_cut_rank"], errors="coerce")
    cutters = cutters[cutters["top_cut_rank_num"].notna()]
    cut_player_tournament = cutters[["tournament_id", "name"]].drop_duplicates().rename(columns={"name": "player"})

    if split_key == "any":
        out = results.copy()
        out["corp_is_tracked"] = True
        out["runner_is_tracked"] = True
        eligible_names = sorted(cut_player_tournament["player"].unique().tolist())
        tournaments = sorted(out["tournament"].dropna().unique().tolist())
        return out, eligible_names, tournaments

    if split_key == "tournament-cutter":
        cut_idx = pd.MultiIndex.from_frame(cut_player_tournament)
        corp_match = results.set_index(["tournament_id", "corp_player"]).index.isin(cut_idx)
        runner_match = results.set_index(["tournament_id", "runner_player"]).index.isin(cut_idx)
        mask = corp_match | runner_match
        out = results.loc[mask].copy()
        corp_idx = pd.MultiIndex.from_arrays([out["tournament_id"], out["corp_player"]])
        runner_idx = pd.MultiIndex.from_arrays([out["tournament_id"], out["runner_player"]])
        out["corp_is_tracked"] = corp_idx.isin(cut_idx)
        out["runner_is_tracked"] = runner_idx.isin(cut_idx)
        eligible_names = sorted(cut_player_tournament["player"].unique().tolist())
        tournaments = sorted(out["tournament"].dropna().unique().tolist())
        return out, eligible_names, tournaments

    if split_key == "any-cutter":
        cut_idx = cut_player_tournament["player"]
        mask = results["corp_player"].isin(cut_idx) | results["runner_player"].isin(cut_idx)
        out = results.loc[mask].copy()
        out["corp_is_tracked"] = out["corp_player"].isin(cut_idx)
        out["runner_is_tracked"] = out["runner_player"].isin(cut_idx)
        eligible_names = sorted(cut_player_tournament["player"].unique().tolist())
        tournaments = sorted(out["tournament"].dropna().unique().tolist())
        return out, eligible_names, tournaments

    m = re.match(r"any-swiss-top(\d+)", split_key)
    if m:
        N = int(m.group(1))
        swiss = standings.copy()
        swiss["swiss_rank_num"] = pd.to_numeric(swiss["swiss_rank"], errors="coerce")
        swiss = swiss[swiss["swiss_rank_num"].notna() & (swiss["swiss_rank_num"] <= N)]
        idx = swiss["name"].drop_duplicates()
        mask = results["corp_player"].isin(idx) | results["runner_player"].isin(idx)
        out = results.loc[mask].copy()
        out["corp_is_tracked"] = out["corp_player"].isin(idx)
        out["runner_is_tracked"] = out["runner_player"].isin(idx)
        eligible_names = sorted(swiss["name"].dropna().unique().tolist())
        tournaments = sorted(out["tournament"].dropna().unique().tolist())
        return out, eligible_names, tournaments

    m = re.match(r"tournament-swiss-top(\d+)", split_key)
    if m:
        N = int(m.group(1))
        swiss = standings.copy()
        swiss["swiss_rank_num"] = pd.to_numeric(swiss["swiss_rank"], errors="coerce")
        swiss = swiss[swiss["swiss_rank_num"].notna() & (swiss["swiss_rank_num"] <= N)]

        # (tournament_id, player) pairs who were top-N in swiss for a specific tournament
        swiss_top_player_tourn = swiss[["tournament_id", "name"]].drop_duplicates().rename(columns={"name": "player"})
        top_idx = pd.MultiIndex.from_frame(swiss_top_player_tourn)

        corp_match = results.set_index(["tournament_id", "corp_player"]).index.isin(top_idx)
        runner_match = results.set_index(["tournament_id", "runner_player"]).index.isin(top_idx)
        mask = corp_match | runner_match
        out = results.loc[mask].copy()

        corp_idx = pd.MultiIndex.from_arrays([out["tournament_id"], out["corp_player"]])
        runner_idx = pd.MultiIndex.from_arrays([out["tournament_id"], out["runner_player"]])
        out["corp_is_tracked"] = corp_idx.isin(top_idx)
        out["runner_is_tracked"] = runner_idx.isin(top_idx)

        eligible_names = sorted(swiss_top_player_tourn["player"].dropna().unique().tolist())
        tournaments = sorted(out["tournament"].dropna().unique().tolist())
        return out, eligible_names, tournaments

    raise ValueError(f"Unknown split_key: {split_key}")


def _corp_vs_runner_matrix(df: pd.DataFrame) -> dict:
    d = df.copy()
    d["result"] = d["result"].astype(str).str.lower()
    d = d[d["result"] != "bye"]

    grp = (
        d.groupby(["corp_id", "runner_id", "runner_faction"], dropna=False)
        .agg(games=("result", "size"), corp_wins=("result", lambda s: (s == "corp").sum()))
        .reset_index()
    )
    grp["winrate"] = grp["corp_wins"] / grp["games"]
    grp.rename(columns={"runner_id": "identity", "runner_faction": "faction"}, inplace=True)

    out = {}
    for corp_name, sub in grp.groupby("corp_id"):
        # sort by games (desc), then winrate (desc), then name
        sub = sub.sort_values(["games", "winrate", "identity"], ascending=[False, False, True]).reset_index(drop=True)
        sub["color"] = sub["faction"].map(faction_colors).fillna("#cccccc")
        sub["alpha"] = 1.0
        sub["winrate_pct"] = (sub["winrate"] * 100).round(2)
        payload = {}
        for col in ["identity", "faction", "games", "corp_wins", "winrate", "winrate_pct", "color", "alpha"]:
            vals = sub[col]
            payload[col] = vals.astype(str).tolist() if col in ["identity", "faction", "color"] else vals.tolist()
        payload["_y_factors"] = sub["identity"].astype(str).tolist()
        out[str(corp_name)] = payload
    return out


def _runner_vs_corp_matrix(df: pd.DataFrame) -> dict:
    d = df.copy()
    d["result"] = d["result"].astype(str).str.lower()
    d = d[d["result"] != "bye"]

    grp = (
        d.groupby(["runner_id", "corp_id", "corp_faction"], dropna=False)
        .agg(games=("result", "size"), runner_wins=("result", lambda s: (s == "runner").sum()))
        .reset_index()
    )
    grp["winrate"] = grp["runner_wins"] / grp["games"]
    grp.rename(columns={"corp_id": "identity", "corp_faction": "faction"}, inplace=True)

    out = {}
    for runner_name, sub in grp.groupby("runner_id"):
        # sort by games (desc), then winrate (desc), then name
        sub = sub.sort_values(["games", "winrate", "identity"], ascending=[False, False, True]).reset_index(drop=True)
        sub["color"] = sub["faction"].map(faction_colors).fillna("#cccccc")
        sub["alpha"] = 1.0
        sub["winrate_pct"] = (sub["winrate"] * 100).round(2)
        payload = {}
        for col in ["identity", "faction", "games", "runner_wins", "winrate", "winrate_pct", "color", "alpha"]:
            vals = sub[col]
            payload[col] = vals.astype(str).tolist() if col in ["identity", "faction", "color"] else vals.tolist()
        payload["_y_factors"] = sub["identity"].astype(str).tolist()
        out[str(runner_name)] = payload
    return out


def _df_to_payload(
    df: pd.DataFrame,
    eligible_names: list[Any],
    tournaments: list[str],
    low_p: float,
    top_n: int,
    split_label: str,
) -> dict:
    low_cut = max(1, int(np.ceil(low_p * len(df)))) if len(df) else 1
    corp_stats = _top_n(_agg_identity_winrate(df, "corp"), top_n)
    runner_stats = _top_n(_agg_identity_winrate(df, "runner"), top_n)

    def _enrich(x: pd.DataFrame) -> pd.DataFrame:
        x = _apply_low_game_flags(x, low_cut)
        x["color"] = x["faction"].map(faction_colors).fillna("#cccccc")
        return x

    corp_stats = _enrich(corp_stats)
    runner_stats = _enrich(runner_stats)

    def _pack(x: pd.DataFrame) -> dict:
        x = x.reset_index(drop=True)
        payload = {}
        for col in [
            "identity",
            "faction",
            "games",
            "wins",
            "winrate",
            "winrate_pct",
            "color",
            "alpha",
            "examples",
            "low_label",
        ]:
            vals = x[col] if col in x.columns else []
            payload[col] = (
                vals.astype(str).tolist()
                if col in ["identity", "faction", "examples", "color", "low_label"]
                else vals.tolist()
            )
        payload["_y_factors"] = x["identity"].astype(str).tolist()
        return payload

    try:
        loser_line = f"<p>Games where loser winrate was below {LOSER_SIDE_MIN_WR*100:.1f}% excluded</p>"
    except NameError:
        loser_line = ""

    footer_html = (
        f"<h3>Notes!</h3>"
        f"<p>Split type: {split_label}</p>"
        f"<p>Following {len(eligible_names)} players</p>"
        f"<p>Low game cut off (transparent bars): {low_cut} games ({LOW_GAME_CUTOFF_P*100:.1f}% of {len(df)} total games)</p>"
        f"<p>Byes and IDs are excluded</p>"
        f"{loser_line}"
        f"<p>Tournaments ({len(tournaments)}):</p>" + "".join(f"<p>&nbsp;&nbsp;- {t}</p>" for t in tournaments)
    )

    corp_matchups = _corp_vs_runner_matrix(df)
    runner_matchups = _runner_vs_corp_matrix(df)

    return {
        "corp": _pack(corp_stats),
        "runner": _pack(runner_stats),
        "footer_html": footer_html,
        "corp_matchups": corp_matchups,
        "runner_matchups": runner_matchups,
    }


split_keys = [
    "any",
    "any-cutter",
    "any-swiss-top16",
    "any-swiss-top24",
    "any-swiss-top32",
    "tournament-cutter",
    "tournament-swiss-top16",
    "tournament-swiss-top24",
    "tournament-swiss-top32",
]

# Precompute
TOP_N = 15
payloads = {}
for key in split_keys:
    df_split, eligible_names, tourns = _build_flags_for_split(key)
    payloads[key] = _df_to_payload(df_split, eligible_names, tourns, LOW_GAME_CUTOFF_P, TOP_N, split_label=key)

# Default = first button
default_key = split_keys[0]
corp_src = ColumnDataSource(payloads[default_key]["corp"])
runner_src = ColumnDataSource(payloads[default_key]["runner"])

# Matchup sources start with the first item of each side
first_corp = corp_src.data["identity"][0]
first_runner = runner_src.data["identity"][0]

corp_match_src = ColumnDataSource(payloads[default_key]["corp_matchups"].get(first_corp, {}))
runner_match_src = ColumnDataSource(payloads[default_key]["runner_matchups"].get(first_runner, {}))


def make_side_wr_chart(src: ColumnDataSource, title: str):
    cats = src.data.get("_y_factors", [])
    p = figure(
        height=max(450, 30 * max(3, len(cats))),
        sizing_mode="stretch_width",
        y_range=cats,
        x_range=(0, 1),
        title=title,
        toolbar_location="above",
        tools="tap,reset,save",
    )
    bars = p.hbar(y="identity", right="winrate", height=0.7, source=src, color="color", alpha="alpha")

    p.add_tools(
        HoverTool(
            renderers=[bars],
            tooltips="""
            <div style="font-size: 12px; line-height: 1.25;">
              <div><b>@identity</b></div>
              <div><b>Win rate:</b> @winrate_pct%</div>
              <div><b>Wins/Games:</b> @wins / @games @{low_label}{safe}</div>
              <div style="margin-top:4px;"><b>Examples:</b><br>@examples{safe}</div>
            </div>
            """,
            # <div><b>Faction:</b> @faction</div>
        )
    )
    p.xaxis.axis_label = "Win rate"
    p.xaxis.formatter = NumeralTickFormatter(format="0%")
    p.yaxis.axis_label = ""
    p.outline_line_color = None
    return p


def make_matchup_chart(src: ColumnDataSource, title: str, side: str):
    cats = src.data.get("_y_factors", [])
    p = figure(
        height=max(450, 26 * max(3, len(cats))),
        sizing_mode="stretch_width",
        y_range=cats,
        x_range=(0, 1),
        title=title,
        toolbar_location="above",
        tools="reset,save",
    )
    bars = p.hbar(y="identity", right="winrate", height=0.7, source=src, color="color", alpha="alpha")

    p.add_tools(
        HoverTool(
            renderers=[bars],
            tooltips=f"""
            <div style="font-size:12px; line-height:1.25;">
              <div><b>@identity</b></div>
              <div><b>Win Rate:</b> @winrate_pct%</div>
              <div><b>Wins/Games:</b> @{side}_wins / @games</div>
            </div>
            """,
        )
    )
    p.xaxis.axis_label = "Win Rate"
    p.xaxis.formatter = NumeralTickFormatter(format="0%")
    p.yaxis.axis_label = ""
    p.x_range.start = 0
    p.outline_line_color = None
    return p


# Figures
p_corp = make_side_wr_chart(corp_src, "Corp")
p_runner = make_side_wr_chart(runner_src, "Runner")

p_corp_match = make_matchup_chart(corp_match_src, f"Matchups: {first_corp or '(none)'}", "corp")
p_runner_match = make_matchup_chart(runner_match_src, f"Matchups: {first_runner or '(none)'}", "runner")

footer = Div(text=payloads[default_key]["footer_html"], sizing_mode="stretch_width")

buttons = RadioButtonGroup(labels=split_keys, active=0)

### Hack panels to change data
corp_select_cb = CustomJS(
    args=dict(
        corp_src=corp_src,
        match_src=corp_match_src,
        p_match=p_corp_match,
        matchup_map=payloads[default_key]["corp_matchups"],  # Replaced on change
    ),
    code="""
    const inds = corp_src.selected.indices;
    if (!inds || inds.length === 0) return;
    const i = inds[0];
    const corp_name = corp_src.data['identity'][i];

    const map = matchup_map;
    const payload = map[corp_name] || {identity:[], faction:[], games:[], corp_wins:[], winrate:[], winrate_pct:[], color:[], alpha:[], _y_factors:[]};

    match_src.data = payload;
    p_match.y_range.factors = payload['_y_factors'] || [];
    p_match.title.text = `Matchups: ${corp_name}`;
    match_src.change.emit();
    """,
)
corp_src.selected.js_on_change("indices", corp_select_cb)

runner_select_cb = CustomJS(
    args=dict(
        runner_src=runner_src,
        match_src=runner_match_src,
        p_match=p_runner_match,
        matchup_map=payloads[default_key]["runner_matchups"],  # Replaced on change
    ),
    code="""
    const inds = runner_src.selected.indices;
    if (!inds || inds.length === 0) return;
    const i = inds[0];
    const runner_name = runner_src.data['identity'][i];

    const map = matchup_map;
    const payload = map[runner_name] || {identity:[], faction:[], games:[], runner_wins:[], winrate:[], winrate_pct:[], color:[], alpha:[], _y_factors:[]};

    match_src.data = payload;
    p_match.y_range.factors = payload['_y_factors'] || [];
    p_match.title.text = `Matchups: ${runner_name}`;
    match_src.change.emit();
    """,
)
runner_src.selected.js_on_change("indices", runner_select_cb)

btn_callback = CustomJS(
    args=dict(
        corp_src=corp_src,
        runner_src=runner_src,
        corp_match_src=corp_match_src,
        runner_match_src=runner_match_src,
        p_corp=p_corp,
        p_runner=p_runner,
        p_corp_match=p_corp_match,
        p_runner_match=p_runner_match,
        footer=footer,
        data_map=payloads,
        buttons=buttons,
        corp_select_cb=corp_select_cb,
        runner_select_cb=runner_select_cb,
    ),
    code="""
    const key = buttons.labels[buttons.active];

    // Remember current selections
    let prev_corp_name = null;
    if (corp_src.selected.indices && corp_src.selected.indices.length > 0) {
      const i = corp_src.selected.indices[0];
      prev_corp_name = corp_src.data['identity']?.[i] ?? null;
    }
    let prev_runner_name = null;
    if (runner_src.selected.indices && runner_src.selected.indices.length > 0) {
      const j = runner_src.selected.indices[0];
      prev_runner_name = runner_src.data['identity']?.[j] ?? null;
    }

    // Pull new payloads
    const corp   = data_map[key]["corp"];
    const runner = data_map[key]["runner"];
    const corp_map   = data_map[key]["corp_matchups"];
    const runner_map = data_map[key]["runner_matchups"];

    // Swap corp/runner data
    corp_src.data = corp;
    runner_src.data = runner;

    // Try to re-select the same IDs in the new data
    const corp_ids = corp_src.data['identity'] || [];
    const runner_ids = runner_src.data['identity'] || [];

    let corp_sel_idx = -1;
    if (prev_corp_name) {
      corp_sel_idx = corp_ids.indexOf(prev_corp_name);
    }
    let runner_sel_idx = -1;
    if (prev_runner_name) {
      runner_sel_idx = runner_ids.indexOf(prev_runner_name);
    }

    // Apply selections if found; otherwise keep charts un-tapped
    corp_src.selected.indices = (corp_sel_idx >= 0) ? [corp_sel_idx] : [];
    runner_src.selected.indices = (runner_sel_idx >= 0) ? [runner_sel_idx] : [];

    // Update y-axis categories
    p_corp.y_range.factors = corp["_y_factors"] || [];
    p_runner.y_range.factors = runner["_y_factors"] || [];

    // Update footer
    footer.text = data_map[key]["footer_html"];

    // Populate matchup panels
    // Corp matchup
    let corp_name_for_panel = null;
    if (corp_sel_idx >= 0) {
      corp_name_for_panel = corp_ids[corp_sel_idx];
    } else if (corp_ids.length > 0) {
      corp_name_for_panel = corp_ids[0];
    }

    if (corp_name_for_panel) {
      const payload_c = (corp_map[corp_name_for_panel]) || {identity:[], faction:[], games:[], corp_wins:[], winrate:[], winrate_pct:[], color:[], alpha:[], _y_factors:[]};
      corp_match_src.data = payload_c;
      p_corp_match.y_range.factors = payload_c['_y_factors'] || [];
      p_corp_match.title.text = `Matchups: ${corp_name_for_panel}`;
      corp_match_src.change.emit();
    } else {
      corp_match_src.data = {identity:[], faction:[], games:[], corp_wins:[], winrate:[], winrate_pct:[], color:[], alpha:[], _y_factors:[]};
      p_corp_match.y_range.factors = [];
      p_corp_match.title.text = "Matchups: unselected";
      corp_match_src.change.emit();
    }

    // Runner matchup
    let runner_name_for_panel = null;
    if (runner_sel_idx >= 0) {
      runner_name_for_panel = runner_ids[runner_sel_idx];
    } else if (runner_ids.length > 0) {
      runner_name_for_panel = runner_ids[0];
    }

    if (runner_name_for_panel) {
      const payload_r = (runner_map[runner_name_for_panel]) || {identity:[], faction:[], games:[], runner_wins:[], winrate:[], winrate_pct:[], color:[], alpha:[], _y_factors:[]};
      runner_match_src.data = payload_r;
      p_runner_match.y_range.factors = payload_r['_y_factors'] || [];
      p_runner_match.title.text = `Matchups: ${runner_name_for_panel}`;
      runner_match_src.change.emit();
    } else {
      runner_match_src.data = {identity:[], faction:[], games:[], runner_wins:[], winrate:[], winrate_pct:[], color:[], alpha:[], _y_factors:[]};
      p_runner_match.y_range.factors = [];
      p_runner_match.title.text = "Matchups: unselected";
      runner_match_src.change.emit();
    }

    // Final emit
    corp_src.change.emit();
    runner_src.change.emit();

    //  Update maps for future calls
    corp_select_cb.args['matchup_map'] = corp_map;
    runner_select_cb.args['matchup_map'] = runner_map;
    """,
)
buttons.js_on_change("active", btn_callback)

layout = column(
    buttons,
    row(p_corp, p_corp_match, sizing_mode="stretch_width"),
    row(p_runner, p_runner_match, sizing_mode="stretch_width"),
    footer,
    sizing_mode="stretch_width",
)
show(layout)

# %%
output_file("sides_and_matchups.html", title="Side Performance")
save(layout)

# %%
df_split

# %%
standings

# player_wr_df.loc["pokeking"][("runner", "swiss")]
player_wr_df.loc["pokeking"]

player = "pokeking"
mask = (
    results_unfiltered["corp_player"].str.contains(player, case=False, na=False)
    | results_unfiltered["runner_player"].str.contains(player, case=False, na=False)
) & results_unfiltered["runner_id"].str.contains("Esâ Afontov: Eco-Insurrectionist", case=False, na=False)
results_unfiltered.loc[mask]

mask = (
    results_unfiltered["corp_id"].str.contains("AU Co.: The Gold Standard in Clones", case=False, na=False)
    & results_unfiltered["runner_id"].str.contains("Esâ Afontov: Eco-Insurrectionist", case=False, na=False)
    & results_unfiltered["runner_player"].str.contains("hams", case=False, na=False)
)
results_unfiltered.loc[mask]
