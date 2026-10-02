from CORE.Models import Context, Factors, Option, ScoreBreakdown, ScoringPolicy


#we'll calculate the energy modulated weight here
def effective_effort_weight(policy: ScoringPolicy, energy: int) -> float:
    
    k = policy.energy_sensitivity
    return policy.w_eff * (1 + k * (10 - energy) / 9)

#we'll calculate the raw score here and we'll be using the energy modulated weight we just calculated above
def raw_score(factors: Factors, energy: int, policy: ScoringPolicy) -> float:
    w_eff = effective_effort_weight(policy, energy)
    positive = factors.importance*policy.w_imp + factors.reward*policy.w_rew + factors.urgency*policy.w_urg
    return positive - factors.effort*w_eff

def raw_bounds(policy: ScoringPolicy, energy: int) -> tuple[float, float]:
    w_eff = effective_effort_weight(policy, energy)

    weight_sum = policy.w_urg + policy.w_rew + policy.w_imp
    raw_max = 10 * weight_sum - 1 * w_eff
    raw_min = 1 * weight_sum - 10 * w_eff
    return raw_min, raw_max

def normalize(raw: float, raw_min: float, raw_max: float) -> float:
    if raw_max == raw_min:
        return 50.0
    return 100*(raw - raw_min)/(raw_max-raw_min)

def contributions(factors: Factors, energy: int, policy: ScoringPolicy) -> dict[str, float]:
    w_eff = effective_effort_weight(policy, energy)
    return {
        "importance": factors.importance * policy.w_imp,
        "urgency": factors.urgency * policy.w_urg,
        "reward": factors.reward * policy.w_rew,
        "effort": -factors.effort * w_eff 
    }

def score(option: Option, ctx: Context, policy: ScoringPolicy) -> ScoreBreakdown:
    
    raw = raw_score(option.factors, ctx.energy, policy)
    raw_min, raw_max = raw_bounds(policy, ctx.energy)
    final = normalize(raw, raw_min, raw_max)

    return ScoreBreakdown(
        option_id=option.option_id,
        raw=raw,
        score=final,
        contributions=contributions(option.factors, ctx.energy, policy),
        effort_weight_applied=effective_effort_weight(policy, ctx.energy),
     )