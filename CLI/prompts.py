from dataclasses import * 
#Validation
            
from CORE.Models import Context, Factors, Option


def ask_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        text = input(prompt).strip()

        try:
            value = int(text)
        except ValueError:
            print("Please type a whole number.")
            continue

        if value < lo or value > hi:
            print(f"Please enter a number between {lo} and {hi}.")
            continue

        return value


def prompt_context() -> Context: #Takes context(ctx)

    energy = ask_int("Energy (1-10): ", 1, 10)

    mood = ask_int("Mood (1-10): ", 1, 10)

    return Context(energy=energy, mood=mood)


def prompt_factors() -> Factors: #Factor inputs
    importance = ask_int("  Importance (1-10): ", 1, 10)

    urgency = ask_int("  Urgency (1-10): ", 1, 10)

    effort = ask_int("  Effort (1-10): ", 1, 10)

    reward = ask_int("  Reward (1-10): ", 1, 10)

    return Factors(
        importance=importance,
        urgency=urgency,
        effort=effort,
        reward=reward
    )


def prompt_option(index: int) -> Option | None:

    while True:
        label = input(f"Option {index} - label (Enter to finish): ").strip()

        if label == "":
            return None

        if len(label) > 60:
            print("Please enter a label with 60 characters or fewer.")
            continue

        break

    factors = prompt_factors()

    return Option(
        option_id=f"o{index}",
        label=label,
        factors=factors
    )


def prompt_options() -> list[Option]: #Option count

    options: list[Option] = []

    while len(options) < 6:
        option = prompt_option(len(options) + 1)

        if option is None:
            if len(options) < 2:
                print("Need at least 2 options.")
                continue
            else:
                break

        options.append(option)

    return options



































            
