
from score_calculation import process_data, pick_best_option
from Validation import valopt,valfac,valstr
#   *//  dict1[name_a] = {
#         "importance" : importance_a,
#         "effort" : effort_a
#     }

#     dict1[name_b] = {
#         "importance" : importance_b,
#         "effort" : effort_b
#   
            
def start():
    n = valopt(("Enter the number of options: "))
    dict1 = {}
    for i in range(n):
        name = valstr((f"Enter option {i+1} : "))
        importance = valfac(("Importance: "))
        effort = valfac(("Effort: "))
        urgency = valfac(("urgency: "))
        reward = valfac(("reward: "))
        dict1[name] = { "importance" : importance , "effort" : effort , "urgency" : urgency , "reward" : reward}
    return dict1
data = start()
dict2 = {}
dict2 = {
    "importance" : 3,
    "effort" : 2,
    "urgency" : 4,
    "reward" : 5
}

result = process_data(data,dict2)
best,score = pick_best_option(result)
print("best option: ",best,score)
