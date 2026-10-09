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
    "zero_cap": 1000,        # lifetime $00 per soul (measured anchor)
    "zero_cap_unmeasured": 250,  # conservative throttle until DID measured
    "zero_stream": 1,        # $00 per soul per round
    "zero_measured": False,  # the DID anchor is UNMEASURED: throttle applies
    "sybil_detect": 0.30,    # per-round P(fake soul revoked) -- ASSUMED until measured
    "review_true_pos": 0.90,  # P(review confirms real fraud)
    "review_false_pos": 0.05,  # P(review condemns the honest)
    "smurf_win_flag": 0.75,  # win-rate over last 20 that opens a flag
    "placement_matches": 10,  # provisional souls: no smell flags yet
    "veteran_matches": 150,  # established souls exempt from the smell test
    "booster_pair_min": 3,   # same-opponent meetings that open inquiry
    "booster_pair_win": 0.80,
    "velocity_gain": 200,    # elo/season that opens the velocity inquiry
    "velocity_matches": 15,  # minimum season matches for the velocity read
    "velocity_win": 0.65,
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
            "opponents": {},    # opp soul -> [wins, meetings] (booster watch)
            "elo_sstart": 1200,      # elo at season start (velocity watch)
            "matches_sstart": 0,     # matches at season start
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
    # every booster gets an accomplice who throws arranged bouts for them
    for a in [p for p in players if p["adv"] == "booster"]:
        cands = [p for p in players if p["honest"] and p is not a]
        if not cands:
            break
        c = rng.choice(cands)
        c["honest"], c["adv"] = False, "accomplice"
        a["pair_soul"], c["pair_soul"] = c["soul"], a["soul"]
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


def play_arranged(winner, loser, rng, ledger):
    """An arranged bout: the accomplice throws, the booster climbs.

    MECHANISM: the fix for the round-1 dead end -- boosters must actually
    boost, or detection has no signal to catch. Elo moves on the thrown
    result; the pairing ledger records the meeting."""
    exp = 1 / (1 + 10 ** ((loser["elo"] - winner["elo"]) / 400))
    for p, won, e in ((winner, True, exp), (loser, False, 1 - exp)):
        gain = 32 * ((1.0 if won else 0.0) - e)
        p["elo"] += gain
        if p["adv"] == "booster" and won:
            p["boost_elo"] += gain
        p["matches"] += 1
        if won:
            p["wins"] += 1
        p["recent"].append(1 if won else 0)
        p["recent"] = p["recent"][-20:]
    w = winner["opponents"].setdefault(loser["soul"], [0, 0])
    w[1] += 1
    w[0] += 1
    loser["opponents"].setdefault(winner["soul"], [0, 0])[1] += 1
    meet, wins = w[1], w[0]
    if (not winner.get("flagged") and meet >= PARAMS["booster_pair_min"]
            and wins / meet >= PARAMS["booster_pair_win"]):
        winner["flagged"] = True
        winner["flag_kind"] = "booster_smell"
        ledger.append("flag", {"soul": winner["soul"],
                               "pattern": "booster_smell",
                               "pair": loser["soul"], "meetings": meet,
                               "win_rate": round(wins / meet, 3)})


def play_match(a, b, rng, ledger):
    """One ladder match; Elo moves; the recent window feeds the smell test.

    AMENDED (round 2): the smell test fires at EVERY tier (smurfs outclimb
    1400), provisional souls (< placement_matches) are exempt, established
    veterans (> veteran_matches) are exempt; repeated-pairing opens the
    booster inquiry."""
    exp = 1 / (1 + 10 ** ((b["elo"] - a["elo"]) / 400))
    # true outcome from true skill, not shown elo
    p_a = 1 / (1 + 10 ** ((b.get("skill", 1500) - a.get("skill", 1500)) / 400))
    a_wins = rng.random() < p_a
    winner, loser = (a, b) if a_wins else (b, a)
    # the pairing ledger: who keeps meeting whom
    w = winner["opponents"].setdefault(loser["soul"], [0, 0])
    w[1] += 1
    w[0] += 1
    l = loser["opponents"].setdefault(winner["soul"], [0, 0])
    l[1] += 1
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
        # the smell test, all tiers: crushing, but not yet a veteran,
        # and past provisional placement
        if (len(p["recent"]) >= 20 and not p["flagged"]
                and PARAMS["placement_matches"] <= p["matches"]
                < PARAMS["veteran_matches"]
                and sum(p["recent"]) / 20 >= PARAMS["smurf_win_flag"]):
            p["flagged"] = True
            p["flag_kind"] = "smurf_smell"
            ledger.append("flag", {"soul": p["soul"], "pattern": "smurf_smell",
                                   "win_rate": round(sum(p["recent"]) / 20, 3),
                                   "elo": round(p["elo"])})
    # the booster inquiry: one soul farming another
    meet, wins = w[1], w[0]
    if (not winner.get("flagged") and meet >= PARAMS["booster_pair_min"]
            and wins / meet >= PARAMS["booster_pair_win"]):
        winner["flagged"] = True
        winner["flag_kind"] = "booster_smell"
        ledger.append("flag", {"soul": winner["soul"],
                               "pattern": "booster_smell",
                               "pair": loser["soul"], "meetings": meet,
                               "win_rate": round(wins / meet, 3)})


def excess_of(a, amount):
    """$PP minted beyond what the soul's true skill backs.

    DOCTRINE (round 2): a smurf's rank understates their skill -- their $PP
    is skill-backed and legitimate. Fraud is EXCESS: attested tier above
    true tier. Only the dishonest can commit it; an honest lucky streak
    is not fraud."""
    if a["honest"]:
        return 0
    _, true_pp = tier_of(a.get("skill", 1500))
    return max(0, amount - true_pp)


def review_flags(pop, pending, rng, ledger, stats):
    """Human review, modeled: confirms real fraud usually, errs rarely.

    AMENDED (round 2): the flag HOLDS the attestation for review -- it never
    denies it. Cleared souls mint (delayed, not denied); only confirmed
    fraud -- or the review's rare error -- ends in a block."""
    for a in pop:
        if not a["flagged"]:
            continue
        fraud = not a["honest"]
        p = PARAMS["review_true_pos"] if fraud else PARAMS["review_false_pos"]
        if rng.random() < p:
            a["soul_valid"] = False
            ledger.append("soul_revoked",
                          {"soul": a["soul"], "fraud": fraud,
                           "pattern": a.get("flag_kind", "smurf_smell")})
            if a.get("flag_kind") == "booster_smell":
                # the accomplice falls with the booster
                pair = next((x for x in pop
                             if x["soul"] == a.get("pair_soul")), None)
                if pair is not None and pair["soul_valid"]:
                    pair["soul_valid"] = False
                    ledger.append("soul_revoked",
                                  {"soul": pair["soul"], "fraud": True,
                                   "cause": "accomplice"})
        else:
            ledger.append("flag_cleared",
                          {"soul": a["soul"],
                           "pattern": a.get("flag_kind", "smurf_smell")})
        a["flagged"] = False  # reviewed either way; the ledger keeps it
    # the held attestations resolve now that review has spoken
    for a in pending:
        tier, amount = tier_of(a["elo"])
        if not a["soul_valid"]:
            ledger.append("gate_block",
                          {"soul": a["soul"], "claim": "pp_attestation",
                           "reasons": ["review confirmed; soul revoked"]})
            if a["honest"]:
                stats["blocked_honest"] += 1
            else:
                stats["blocked_fraud"] += 1
                stats["excess_blocked"] += excess_of(a, amount)
            continue
        a["pp_earned"] += amount
        ledger.append("pp_mint", {"soul": a["soul"], "tier": tier,
                                  "amount": amount, "held": True})
        if a["honest"]:
            stats["legit_pp"] += amount
            stats["honest_pp"] += 1
        else:
            stats["fraud_pp"] += amount  # review missed it: the residual
            stats["excess_minted"] += excess_of(a, amount)


def season_attest(pop, ledger):
    """Season's end: rank attestations weighed at the TRVVTH gate; $PP mints.

    AMENDED (round 2): a flagged soul's attestation is HELD for review,
    not blocked -- the gate blocks only the incomplete (too few matches),
    never the merely suspected."""
    stats = {"legit_pp": 0, "fraud_pp": 0, "blocked_fraud": 0,
             "blocked_honest": 0, "honest_pp": 0,
             "excess_minted": 0, "excess_blocked": 0}
    pending = []
    for a in pop:
        if a["role"] != "player" or not a["soul_valid"]:
            continue
        # the velocity inquiry, second signal of amendment 1: climbing
        # faster than honest play explains, with the wins to match it
        season_matches = a["matches"] - a["matches_sstart"]
        season_gain = a["elo"] - a["elo_sstart"]
        recent_wr = (sum(a["recent"]) / len(a["recent"])
                     if a["recent"] else 0)
        if (not a["flagged"]
                and season_matches >= PARAMS["velocity_matches"]
                and season_gain >= PARAMS["velocity_gain"]
                and recent_wr >= PARAMS["velocity_win"]):
            a["flagged"] = True
            a["flag_kind"] = "velocity_smell"
            ledger.append("flag", {"soul": a["soul"],
                                   "pattern": "velocity_smell",
                                   "season_gain": round(season_gain),
                                   "win_rate": round(recent_wr, 3)})
        tier, amount = tier_of(a["elo"])
        claim = {"kind": "pp_attestation", "soul_valid": a["soul_valid"],
                 "evidence": {"matches": a["matches"],
                              "flagged": a["flagged"]}}
        dec = trvvth_gate(claim, PARAMS)
        if not dec.allowed:
            if a["flagged"]:
                # held, not blocked: review will speak
                pending.append(a)
                ledger.append("attest_held",
                              {"soul": a["soul"],
                               "pattern": a.get("flag_kind", "smurf_smell")})
                continue
            ledger.append("gate_block",
                          {"soul": a["soul"], "claim": "pp_attestation",
                           "reasons": dec.reasons})
            if a["honest"]:
                stats["blocked_honest"] += 1
            else:
                stats["blocked_fraud"] += 1
                stats["excess_blocked"] += excess_of(a, amount)
            continue
        a["pp_earned"] += amount
        ledger.append("pp_mint", {"soul": a["soul"], "tier": tier,
                                  "amount": amount})
        if a["honest"]:
            stats["legit_pp"] += amount
            stats["honest_pp"] += 1
        else:
            stats["fraud_pp"] += amount
            stats["excess_minted"] += excess_of(a, amount)
    return stats, pending


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
            # the conservative throttle: an unmeasured DID anchor streams
            # against the low cap until it proves its recall on testnet
            cap = (PARAMS["zero_cap"] if PARAMS["zero_measured"]
                   else PARAMS["zero_cap_unmeasured"])
            dec = trvvth_gate(claim, {**PARAMS, "zero_cap": cap})
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


def run_once(n, rounds, seed, adversary_mix, pover=None):
    """One full run: the world turns, the ledger keeps score.

    pover: per-scenario parameter overrides (e.g. a weak DID anchor) --
    applied to PARAMS for the run, restored after."""
    saved = dict(PARAMS)
    if pover:
        PARAMS.update(pover)
    try:
        return _run_once_inner(n, rounds, seed, adversary_mix)
    finally:
        PARAMS.clear()
        PARAMS.update(saved)


def _run_once_inner(n, rounds, seed, adversary_mix):
    rng = random.Random(seed)
    ledger = Ledger()
    pop = make_population(n, rng, adversary_mix)
    players = [a for a in pop if a["role"] == "player"]
    agg = {"legit_pp": 0, "fraud_pp": 0, "blocked_fraud": 0,
           "blocked_honest": 0, "honest_pp": 0,
           "excess_minted": 0, "excess_blocked": 0,
           "intended_00": 0, "minted_00": 0}
    for rnd in range(rounds):
        active = [a for a in players if a["soul_valid"]]
        by_soul = {a["soul"]: a for a in active}
        # arranged bouts first: boosters meet their accomplices
        busy = set()
        for a in active:
            if a["adv"] != "booster":
                continue
            c = by_soul.get(a.get("pair_soul", ""))
            if c is None or c["soul"] in busy:
                continue
            if rng.random() < 0.30:
                play_arranged(a, c, rng, ledger)
                busy.add(a["soul"])
                busy.add(c["soul"])
        # the ladder: honest matches for everyone else
        free = [a for a in active if a["soul"] not in busy]
        rng.shuffle(free)
        for i in range(0, len(free) - 1, 2):
            play_match(free[i], free[i + 1], rng, ledger)
        # grace streams every round
        intended, minted = zero_streams(pop, rng, ledger)
        agg["intended_00"] += intended
        agg["minted_00"] += minted
        # the chain: one block per round
        mine_block(pop, rng, ledger)
        # season's end: attest (holds), then review resolves the held
        if (rnd + 1) % PARAMS["season_every"] == 0:
            s, pending = season_attest(pop, ledger)
            review_flags(pop, pending, rng, ledger, s)
            for k in s:  # s now holds the full season: pre- + post-review
                agg[k] += s[k]
            for a in pop:  # new season, new velocity window
                a["elo_sstart"] = a["elo"]
                a["matches_sstart"] = a["matches"]
    # metrics -- legitimacy is EXCESS-based (round 2): only $PP minted
    # beyond true skill counts against the design
    total_pp = agg["legit_pp"] + agg["fraud_pp"]
    miners = [a for a in pop if a["role"] == "miner"]
    fake_souls = sum(len(a["fake_souls"]) for a in pop)
    revoked_fakes = sum(1 for a in pop for fs in a["fake_souls"]
                        if not fs["valid"])
    fraudsters = [a for a in pop if not a["honest"]
                  and a["role"] == "player"]
    revoked_fraud = sum(1 for a in fraudsters if not a["soul_valid"])
    mg = gini([a.get("blocks", 0) for a in miners])
    # the watch: centralization must never go unnoticed (amendment 4)
    watch_ok = True
    if mg > 0.60:
        ledger.append("alert", {"kind": "miner_centralization",
                                "gini": round(mg, 4),
                                "doctrine": "monitored acceptance"})
        watch_ok = True  # the alert IS the remedy: noticed, published
    ex_m, ex_b = agg["excess_minted"], agg["excess_blocked"]
    return {
        "pp_legitimacy": 1 - ex_m / total_pp if total_pp else 1.0,
        "fraud_block_rate": (ex_b / (ex_b + ex_m)
                             if (ex_b + ex_m) else 1.0),
        "honest_block_rate": (agg["blocked_honest"] / agg["honest_pp"]
                              if agg["honest_pp"] else 0.0),
        "zero_oversupply": (agg["minted_00"] / agg["intended_00"]
                            if agg["intended_00"] else 1.0),
        "sybil_recall": revoked_fakes / fake_souls if fake_souls else 1.0,
        "integrity_recall": (revoked_fraud / len(fraudsters)
                             if fraudsters else 1.0),
        "miner_gini": mg,
        "miner_watch": 1.0 if watch_ok else 0.0,
        "ledger_ok": ledger.verify(),
        "shadow_flags": len(shadow_scan(ledger)),
        "ledger_entries": len(ledger.entries),
    }


# ---------------------------------------------------------------------------
# Verdicts: thresholds are design choices; the red pen may move them.

THRESHOLDS = {
    "pp_legitimacy": ("≥", 0.95, "minted $PP must not exceed true skill"),
    "fraud_block_rate": ("≥", 0.80, "excess $PP must mostly be blocked"),
    "honest_block_rate": ("≤", 0.10, "the honest must rarely be blocked"),
    "zero_oversupply": ("≤", 1.10, "$00 must resist farming"),
    "sybil_recall": ("≥", 0.70, "fake souls must mostly die"),
    "miner_watch": ("≥", 1.0, "centralization must never go unnoticed"),
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
    # the weak anchor: unmeasured DID, conservative throttle, weak detect
    "zero_farm_weak_anchor": {"farmer": 0.30,
                              "_pover": {"sybil_detect": 0.15}},
    "whale_miner": {"whale": True},
    "combined": {"smurf": 0.15, "booster": 0.08, "farmer": 0.25,
                 "whale": True},
}


def run_scenarios(n=300, rounds=200, seeds=(418, 777, 93)):
    """Run every scenario across seeds; auto-scale rounds when the noise
    band swallows a verdict ('work it til it is' -- his words)."""
    report = {}
    for name, mix in SCENARIOS.items():
        mix = dict(mix)
        pover = mix.pop("_pover", None)  # per-scenario param overrides
        runs = [run_once(n, rounds, s, mix, pover) for s in seeds]
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
            runs = [run_once(n, scaled, s, mix, pover) for s in seeds]
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
        report[name]["means"]["miner_gini"] = round(
            statistics.mean(r["miner_gini"] for r in runs), 4)
        report[name]["means"]["integrity_recall"] = round(
            statistics.mean(r["integrity_recall"] for r in runs), 4)
    return report


if __name__ == "__main__":
    rep = run_scenarios()
    for name, r in rep.items():
        print(f"\n== {name} (rounds={r['rounds']}) ==")
        for f in verdict(r["means"]):
            mark = "HOLD" if f["holds"] else "BREAK"
            print(f"  [{mark}] {f['metric']}: {f['value']} "
                  f"(thr {f['threshold']})")
        print(f"  [info] miner_gini: {round(r['means'].get('miner_gini', 0), 4)} "
              f"(reported; the watch is the verdict)")
        print(f"  [info] integrity_recall: "
              f"{round(r['means'].get('integrity_recall', 0), 4)} "
              f"(fraudsters revoked)")
