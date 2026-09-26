def pick_winner(name_a, score_a, name_b, score_b):
    if score_a == score_b:
        return ("Equal")
    elif score_a > score_b:
        return (f"Consider: {name_a}")
    else:
        return (f"Consider: {name_b}")

    


result = pick_winner("Study", 9, "Game", 2)
print(result)
