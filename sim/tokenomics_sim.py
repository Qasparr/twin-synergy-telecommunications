#!/usr/bin/env python3
# Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure
# All Rights Reserved, Without Prejudice · CashApp $axoneme
# 93
#
# tokenomics_sim.py -- agent-based simulation of the Twin Synergy
#   tokenomics trinity: the Miner, $PP "proof positive", $00.
#
# EPIGRAPH: "By their fruits ye shall know them." -- Matthew 7:16
# DATE:     Sol in Libra, 2026 e.v.
#
# HYPOTHESIS: a population of PERSONA V-composed agents -- miners, ladder
#   players, newcomers, and adversaries (smurfs, boosters, $00 farmers,
#   whale miners) -- run through the TRVVTH gate round by round, will
#   show whether the tokenization holds: does $PP stay backed by real
#   skill, does $00 resist farming, does the miner tier stay honest.
# METHOD:    discrete rounds; Elo ladder with tiered $PP attestation;
#   per-soul $00 streams with sybil detection; hashpower-weighted block
#   lottery; every claim through the TRVVTH gate (fail-closed); every
#   mint on a hash-chained ledger; shadow analysis over the ledger;
#   scenarios x seeds; verdicts against stated thresholds; auto-scale
#   rounds when the noise band swallows the verdict ("work it til it is").
# OBSERVATION: run_scenarios() prints the verdict table.
# RESULT:    SIMULATION-REPORT.md -- does the design hold, and what must
#   change if it does not.
#
# MECHANISM: agents are light dicts (trade/flavor/name/tuners/moon drawn
#   from the persona-v canon via the same loaders the Ten used). The
#   TRVVTH gate checks identity, evidence, and rate limits -- incomplete
#   claims are BLOCKED and recorded, never silently dropped. The ledger
#   is hash-chained JSONL in memory (stdlib only).
# DOCTRINE:  parameters are stated, not hidden; thresholds are design
#   choices the red pen may move. The simulation tests the design, never
#   the people -- adversaries are roles, not accusations.
#
# 93 93/93 -- Love is the law, love under will.

"""Agent-based simulation of the $PP/$00 tokenomics trinity."""

import hashlib
import json
import math
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "persona-v"))
from persona_v import grimoire  # noqa: E402
from persona_v.assignment import load_jobs  # noqa: E402

# ---------------------------------------------------------------------------
# PERSONA V composition (light): every agent wears the mask.

_SENSES = ("sight", "hearing", "touch", "taste", "smell")
_FLAVORS = None
_NAMES = None
_JOBS = None


def _canon():
    """MECHANISM: load the canon once; the agents draw from the same well."""
    global _FLAVORS, _NAMES, _JOBS
    if _FLAVORS is None:
        _FLAVORS = grimoire.load_flavors()
        _NAMES = grimoire.load_names()
        _JOBS = load_jobs()
    return _FLAVORS, _NAMES, _JOBS


def compose_persona(rng):
    """One PERSONA V composition: trade, name, flavor, tuners, moon."""
    flavors, names, jobs = _canon()
    trade = rng.randrange(22)
    flavor = rng.choice(flavors)
    officer = rng.choice([n for n in names if n.flavor == flavor.number] or names)
    sense = rng.choice(_SENSES)
    tuners = {s: (2.0 if s == sense else 1.0) for s in _SENSES}
    return {
        "trade": jobs[trade]["trade"],
        "name": officer.name,
        "office": officer.office,
        "flavor": flavor.name,
        "sense": sense,
        "tuners": tuners,
        "moon": rng.randrange(1, 14),
    }


# ---------------------------------------------------------------------------
# TRVVTH gate: every claim is weighed; the incomplete is blocked, recorded.

class GateDecision:
    __slots__ = ("allowed", "reasons")

    def __init__(self, allowed, reasons):
        self.allowed = allowed
        self.reasons = reasons


def trvvth_gate(claim, ctx):
    """Weigh a claim. Fail-closed: any missing warrant blocks the claim,
    and the block itself is recorded as data."""
    reasons = []
    if not claim.get("soul_valid", False):
        reasons.append("soul invalid or revoked")
    if claim["kind"] == "pp_attestation":
        ev = claim["evidence"]
        if ev["matches"] < ctx["min_matches"]:
            reasons.append(f"only {ev['matches']} matches; need {ctx['min_matches']}")
        if ev["flagged"]:
            reasons.append("ladder-integrity flag open; held for review")
    elif claim["kind"] == "zero_stream":
        if claim["evidence"]["lifetime"] >= ctx["zero_cap"]:
            reasons.append("lifetime $00 cap reached")
    if reasons:
        return GateDecision(False, reasons)
    return GateDecision(True, ["complete"])


# ---------------------------------------------------------------------------
# Ledger: hash-chained, stdlib only. Shadow: analysis over the chain.

class Ledger:
    """MECHANISM: each entry commits to the previous hash; tampering with
    history breaks the chain audibly."""

    def __init__(self):
        self.entries = []
        self.prev = "GENESIS"

    def append(self, kind, data):
        body = json.dumps({"kind": kind, "data": data,
                           "prev": self.prev}, sort_keys=True)
        h = hashlib.sha256(body.encode()).hexdigest()
        self.entries.append({"hash": h, "kind": kind, "data": data,
                             "prev": self.prev})
        self.prev = h

    def verify(self):
        prev = "GENESIS"
        for e in self.entries:
            body = json.dumps({"kind": e["kind"], "data": e["data"],
                               "prev": e["prev"]}, sort_keys=True)
            if e["prev"] != prev:
                return False
            if hashlib.sha256(body.encode()).hexdigest() != e["hash"]:
                return False
            prev = e["hash"]
        return True


def shadow_scan(ledger):
    """DOCTRINE: shadow does not judge; it flags patterns for review."""
    flags = []
    pp_by_soul = {}
    for e in ledger.entries:
        if e["kind"] == "pp_mint":
            s = e["data"]["soul"]
            pp_by_soul.setdefault(s, []).append(e["data"]["amount"])
    for soul, mints in pp_by_soul.items():
        if len(mints) >= 3 and sum(mints) > 200:
            flags.append({"soul": soul, "pattern": "pp_velocity",
                          "detail": f"{len(mints)} mints totaling {sum(mints)}"})
    return flags


# ---------------------------------------------------------------------------
# The world: miners, players, newcomers, adversaries.

TIERS = [  # (elo_floor, name, pp_per_season)
    (2200, "Grandmaster", 100),
    (2000, "Master", 50),
    (1800, "Diamond", 25),
    (1600, "Platinum", 12),
    (1400, "Gold", 6),
    (1200, "Silver", 3),
    (0, "Bronze", 1),
]

PARAMS = {
    "min_matches": 20,       # matches before a rank attestation may be weighed
    "zero_cap": 1000,        # lifetime $00 per soul
    "zero_stream": 1,        # $00 per soul per round
    "sybil_detect": 0.30,    # per-round P(fake soul revoked) -- DID strength
    "review_true_pos": 0.90,  # P(review confirms real fraud)
    "review_false_pos": 0.05,  # P(review condemns the honest)
    "smurf_win_flag": 0.75,  # win-rate over last 20 that opens a flag
    "season_every": 20,      # rounds per season
    "block_reward": 50,
}


def tier_of(elo):
    for floor, name, pp in TIERS:
        if elo >= floor:
            return name, pp
    return "Bronze", 1


def make_population(n, rng, adversary_mix):
    """MECHANISM: roles split 15% miners / 60% players / 25% newcomers;
    adversaries are drawn from the player/newcomer pools per the mix."""
    flavors, names, jobs = _canon()
    pop = []
    for i in range(n):
        r = rng.random()
        role = "miner" if r < 0.15 else ("player" if r < 0.75 else "newcomer")
        a = {
            "pid": i,
            "soul": f"soul-{i}",
            "persona": compose_persona(rng),
            "role": role,
            "honest": True,
            "adv": None,
            "elo": 1200,
            "wins": 0,
            "matches": 0,
            "recent": [],       # last-20 win/loss for the smell test
            "flagged": False,
            "pp_earned": 0,
            "zero_earned": 0,
            "fake_souls": [],   # sybil identities (farmers)
            "soul_valid": True,
        }
        if role == "miner":
            a["hashpower"] = rng.paretovariate(2.0)
        if role == "player":
            a["skill"] = max(800, min(2600, rng.gauss(1500, 300)))
        pop.append(a)
    # seed adversaries
    players = [a for a in pop if a["role"] == "player"]
    newcomers = [a for a in pop if a["role"] == "newcomer"]
    n_smurf = int(len(players) * adversary_mix.get("smurf", 0))
    n_boost = int(len(players) * adversary_mix.get("booster", 0))
    n_farm = int(len(newcomers) * adversary_mix.get("farmer", 0))
    for a in rng.sample(players, min(n_smurf, len(players))):
        a["honest"], a["adv"] = False, "smurf"
        a["skill"] = rng.gauss(2100, 150)  # high skill, low rank: the tell
        a["elo"] = 1100
    for a in rng.sample([p for p in players if p["honest"]],
                        min(n_boost, len(players))):
        a["honest"], a["adv"] = False, "booster"
        a["boost_elo"] = 0  # illegitimate elo, tracked apart
    for a in rng.sample(newcomers, min(n_farm, len(newcomers))):
        a["honest"], a["adv"] = False, "farmer"
        a["fake_souls"] = [
            {"soul": f"soul-{a['pid']}-fake-{k}", "valid": True,
             "lifetime": 0}
            for k in range(rng.randint(2, 5))
        ]
    if adversary_mix.get("whale"):
        w = max([a for a in pop if a["role"] == "miner"],
                key=lambda a: a["hashpower"])
        w["hashpower"] = sum(a["hashpower"] for a in pop
                             if a["role"] == "miner") * 1.2
        w["honest"], w["adv"] = False, "whale"
    return pop


def play_match(a, b, rng, ledger):
    """One ladder match; Elo moves; the recent window feeds the smell test."""
    exp = 1 / (1 + 10 ** ((b["elo"] - a["elo"]) / 400))
    # true outcome from true skill, not shown elo
    p_a = 1 / (1 + 10 ** ((b.get("skill", 1500) - a.get("skill", 1500)) / 400))
    a_wins = rng.random() < p_a
    for p, won, e in ((a, a_wins, exp), (b, not a_wins, 1 - exp)):
        score = 1.0 if won else 0.0
        gain = 32 * (score - e)
        p["elo"] += gain
        if p["adv"] == "booster" and won:
            p["boost_elo"] += gain  # the illegitimate share, tracked
        p["matches"] += 1
        p["wins"] += 1 if won else 0
        p["recent"].append(1 if won else 0)
        p["recent"] = p["recent"][-20:]
        # the smell test: crushing far below one's station
        if (len(p["recent"]) >= 20 and not p["flagged"]
                and sum(p["recent"]) / 20 >= PARAMS["smurf_win_flag"]
                and p["elo"] < 1400):
            p["flagged"] = True
            ledger.append("flag", {"soul": p["soul"], "pattern": "smurf_smell",
                                   "win_rate": sum(p["recent"]) / 20,
                                   "elo": round(p["elo"])})


def review_flags(pop, rng, ledger):
    """Human review, modeled: confirms real fraud usually, errs rarely."""
    for a in pop:
        if not a["flagged"]:
            continue
        fraud = not a["honest"]
        p = PARAMS["review_true_pos"] if fraud else PARAMS["review_false_pos"]
        if rng.random() < p:
            a["soul_valid"] = False
            ledger.append("soul_revoked",
                          {"soul": a["soul"], "fraud": fraud})
        a["flagged"] = False  # reviewed either way; the ledger keeps it


def season_attest(pop, ledger):
    """Season's end: rank attestations weighed at the TRVVTH gate; $PP mints."""
    stats = {"legit_pp": 0, "fraud_pp": 0, "blocked_fraud": 0,
             "blocked_honest": 0, "honest_pp": 0}
    for a in pop:
        if a["role"] != "player" or not a["soul_valid"]:
            continue
        tier, amount = tier_of(a["elo"])
        claim = {"kind": "pp_attestation", "soul_valid": a["soul_valid"],
                 "evidence": {"matches": a["matches"],
                              "flagged": a["flagged"]}}
        dec = trvvth_gate(claim, PARAMS)
        if not dec.allowed:
            ledger.append("gate_block",
                          {"soul": a["soul"], "claim": "pp_attestation",
                           "reasons": dec.reasons})
            if a["honest"]:
                stats["blocked_honest"] += 1
            else:
                stats["blocked_fraud"] += 1
            continue
        a["pp_earned"] += amount
        ledger.append("pp_mint", {"soul": a["soul"], "tier": tier,
                                  "amount": amount})
        if a["honest"]:
            stats["legit_pp"] += amount
            stats["honest_pp"] += 1
        else:
            stats["fraud_pp"] += amount
    return stats


def zero_streams(pop, rng, ledger):
    """$00 grace streams; farmers' fake souls face the DID sybil check."""
    intended, minted = 0, 0
    for a in pop:
        souls = [{"soul": a["soul"], "valid": a["soul_valid"],
                  "fake": False, "ref": a}]
        for fs in a["fake_souls"]:
            souls.append({"soul": fs["soul"], "valid": fs["valid"],
                          "fake": True, "ref": fs})
        for s in souls:
            if not s["valid"]:
                continue
            if not s["fake"]:
                intended += PARAMS["zero_stream"]
            # the sybil check bites fake souls
            if s["fake"] and rng.random() < PARAMS["sybil_detect"]:
                s["ref"]["valid"] = False
                ledger.append("soul_revoked",
                              {"soul": s["soul"], "fraud": True,
                               "cause": "sybil"})
                continue
            claim = {"kind": "zero_stream", "soul_valid": s["valid"],
                     "evidence": {"lifetime": s["ref"].get("zero_earned", 0)
                                  if not s["fake"] else s["ref"]["lifetime"]}}
            dec = trvvth_gate(claim, PARAMS)
            if not dec.allowed:
                ledger.append("gate_block",
                              {"soul": s["soul"], "claim": "zero_stream",
                               "reasons": dec.reasons})
                continue
            if s["fake"]:
                s["ref"]["lifetime"] += PARAMS["zero_stream"]
            else:
                a["zero_earned"] += PARAMS["zero_stream"]
            minted += PARAMS["zero_stream"]
            ledger.append("zero_mint", {"soul": s["soul"],
                                        "fake": s["fake"],
                                        "amount": PARAMS["zero_stream"]})
    return intended, minted


def mine_block(pop, rng, ledger):
    """One block; the lottery weighs hashpower."""
    miners = [a for a in pop if a["role"] == "miner"]
    total = sum(a["hashpower"] for a in miners)
    pick = rng.random() * total
    acc = 0
    for a in miners:
        acc += a["hashpower"]
        if acc >= pick:
            a["blocks"] = a.get("blocks", 0) + 1
            ledger.append("block", {"soul": a["soul"],
                                    "reward": PARAMS["block_reward"]})
            return a
    return miners[-1]


def gini(values):
    """The inequality of the miner tier."""
    v = sorted(values)
    n = len(v)
    if n == 0 or sum(v) == 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(v))
    return (2 * cum) / (n * sum(v)) - (n + 1) / n


def run_once(n, rounds, seed, adversary_mix):
    """One full run: the world turns, the ledger keeps score."""
    rng = random.Random(seed)
    ledger = Ledger()
    pop = make_population(n, rng, adversary_mix)
    players = [a for a in pop if a["role"] == "player"]
    agg = {"legit_pp": 0, "fraud_pp": 0, "blocked_fraud": 0,
           "blocked_honest": 0, "honest_pp": 0,
           "intended_00": 0, "minted_00": 0}
    for rnd in range(rounds):
        # the ladder: a round of matches
        rng.shuffle(players)
        for i in range(0, len(players) - 1, 2):
            play_match(players[i], players[i + 1], rng, ledger)
        # grace streams every round
        intended, minted = zero_streams(pop, rng, ledger)
        agg["intended_00"] += intended
        agg["minted_00"] += minted
        # the chain: one block per round
        mine_block(pop, rng, ledger)
        # season's end: attest, review
        if (rnd + 1) % PARAMS["season_every"] == 0:
            s = season_attest(pop, ledger)
            for k in s:
                agg[k] += s[k]
            review_flags(pop, rng, ledger)
    # metrics
    total_pp = agg["legit_pp"] + agg["fraud_pp"]
    miners = [a for a in pop if a["role"] == "miner"]
    fake_souls = sum(len(a["fake_souls"]) for a in pop)
    revoked_fakes = sum(1 for a in pop for fs in a["fake_souls"]
                        if not fs["valid"])
    return {
        "pp_legitimacy": agg["legit_pp"] / total_pp if total_pp else 1.0,
        "fraud_block_rate": (agg["blocked_fraud"] /
                             (agg["blocked_fraud"] + agg["fraud_pp"])
                             if (agg["blocked_fraud"] + agg["fraud_pp"]) else 1.0),
        "honest_block_rate": (agg["blocked_honest"] / agg["honest_pp"]
                              if agg["honest_pp"] else 0.0),
        "zero_oversupply": (agg["minted_00"] / agg["intended_00"]
                            if agg["intended_00"] else 1.0),
        "sybil_recall": revoked_fakes / fake_souls if fake_souls else 1.0,
        "miner_gini": gini([a.get("blocks", 0) for a in miners]),
        "ledger_ok": ledger.verify(),
        "shadow_flags": len(shadow_scan(ledger)),
        "ledger_entries": len(ledger.entries),
    }


# ---------------------------------------------------------------------------
# Verdicts: thresholds are design choices; the red pen may move them.

THRESHOLDS = {
    "pp_legitimacy": ("≥", 0.95, "rank attestations must stay skill-backed"),
    "fraud_block_rate": ("≥", 0.80, "most fraud must be caught at the gate"),
    "honest_block_rate": ("≤", 0.10, "the honest must rarely be blocked"),
    "zero_oversupply": ("≤", 1.10, "$00 must resist farming"),
    "sybil_recall": ("≥", 0.70, "fake souls must mostly die"),
    "miner_gini": ("≤", 0.60, "mining must not centralize past remedy"),
}


def verdict(metrics):
    """DOCTRINE: the verdict measures convergence; it does not vote."""
    findings = []
    for key, (op, thr, note) in THRESHOLDS.items():
        v = metrics[key]
        ok = (v >= thr) if op == "≥" else (v <= thr)
        findings.append({"metric": key, "value": round(v, 4),
                         "threshold": f"{op} {thr}", "holds": ok,
                         "note": note})
    return findings


SCENARIOS = {
    "baseline": {},
    "smurf_invasion": {"smurf": 0.20},
    "booster_ring": {"booster": 0.10},
    "zero_farm": {"farmer": 0.30},
    "whale_miner": {"whale": True},
    "combined": {"smurf": 0.15, "booster": 0.08, "farmer": 0.25,
                 "whale": True},
}


def run_scenarios(n=300, rounds=200, seeds=(418, 777, 93)):
    """Run every scenario across seeds; auto-scale rounds when the noise
    band swallows a verdict ('work it til it is' -- his words)."""
    report = {}
    for name, mix in SCENARIOS.items():
        runs = [run_once(n, rounds, s, mix) for s in seeds]
        means, stds = {}, {}
        for key in THRESHOLDS:
            vals = [r[key] for r in runs]
            means[key] = statistics.mean(vals)
            stds[key] = statistics.stdev(vals) if len(vals) > 1 else 0.0
        # noise check: if any verdict sits inside its own noise band,
        # double the rounds (twice max) and re-run that scenario
        needy = False
        for key, (op, thr, _) in THRESHOLDS.items():
            margin = abs(means[key] - thr)
            if stds[key] > 0 and margin < stds[key]:
                needy = True
        scaled = rounds
        while needy and scaled < rounds * 4:
            scaled *= 2
            runs = [run_once(n, scaled, s, mix) for s in seeds]
            needy = False
            for key, (op, thr, _) in THRESHOLDS.items():
                vals = [r[key] for r in runs]
                means[key] = statistics.mean(vals)
                stds[key] = statistics.stdev(vals) if len(vals) > 1 else 0.0
                if stds[key] > 0 and abs(means[key] - thr) < stds[key]:
                    needy = True
        report[name] = {"means": means, "stds": stds,
                        "rounds": scaled,
                        "ledger_ok": all(r["ledger_ok"] for r in runs)}
    return report


if __name__ == "__main__":
    rep = run_scenarios()
    for name, r in rep.items():
        print(f"\n== {name} (rounds={r['rounds']}) ==")
        for f in verdict(r["means"]):
            mark = "HOLD" if f["holds"] else "BREAK"
            print(f"  [{mark}] {f['metric']}: {f['value']} "
                  f"(thr {f['threshold']})")
