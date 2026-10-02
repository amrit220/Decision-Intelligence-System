from CORE.Models import ScoringPolicy
from CORE.scoring import score
from CLI.prompts import prompt_context, prompt_options


BALANCED = ScoringPolicy(
    w_imp=0.30, w_urg=0.30, w_rew=0.20, w_eff=0.20,
    energy_sensitivity=0.5, mode_name="balanced",
)

def main():
    ctx = prompt_context()
    options = prompt_options()

    print(f"\n  energy={ctx.energy}  mood={ctx.mood}\n")

    results = [(o, score(o, ctx, BALANCED)) for o in options]
    results.sort(key=lambda pair: pair[1].score, reverse=True)

    for rank, (opt, bd) in enumerate(results, start=1):
        print(f"  {rank}. {opt.label:<20} {bd.score:5.1f} / 100")

    top, best = results[0]
    print(f"\n  RECOMMENDED: {top.label} — {best.score:.1f} / 100")
    print(f"  (next best: {results[1][0].label}, {results[1][1].score:.1f})\n")

    print("  Why:")
    for factor, points in sorted(
        best.contributions.items(), key=lambda kv: abs(kv[1]), reverse=True
    ):
        print(f"    {factor:<12} {points:+.2f}")

if __name__ == "__main__":
    main()