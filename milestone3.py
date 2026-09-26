def pick_winner(name_a, score_a, name_b, score_b):
    if score_a == score_b:
        return ("Equal")
    elif score_a > score_b:
        return (f"Consider: {name_a}")
    else:
        return (f"Consider: {name_b}")

def score_cal(dict1):
     
    names = list(dict1.keys())

    name_a = names[0]
    name_b = names[1]
    name_a_score = dict1[name_a]["importance"]*2 - dict1[name_a]["effort"]
    name_b_score = dict1[name_b]["importance"]*2 - dict1[name_b]["effort"]
    result = pick_winner(name_a, name_a_score, name_b, name_b_score)
    print(result)


def start_DIS():
    dict1 = {}
    name_a = str(input("Enter option 1: "))
    importance_a = int(input("Importance: "))
    effort_a = int(input("Effort: "))

    name_b = str(input("Enter option 2: "))
    importance_b = int(input("Importance: "))
    effort_b = int(input("Effort: "))

    dict1[name_a] = {
        "importance" : importance_a,
        "effort" : effort_a
    }

    dict1[name_b] = {
        "importance" : importance_b,
        "effort" : effort_b
    }

    score_cal(dict1)

    return 0

start_DIS()