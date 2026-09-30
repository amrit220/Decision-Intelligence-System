
from score_calculation import process_data, pick_best_option
#   *//  dict1[name_a] = {
#         "importance" : importance_a,
#         "effort" : effort_a
#     }

#     dict1[name_b] = {
#         "importance" : importance_b,
#         "effort" : effort_b
#     
def valstr(text):
    while True:
        try:
            value = input(text)
            if value.strip() == "":
                raise ValueError
            if not value[0].isalpha():
                raise ValueError
            return value
        except ValueError:
            print("INVALID String, Please enter a Valid String: ")
            
def valint(text):
    while True:
        try:
            value = int(input(text))
            return value    
        except ValueError:
            print("INVALID INPUT, Please enter a Number: ")

            
            
            

def start():
    n = valint(("Enter the number of options: "))
    dict1 = {}
    for i in range(n):
        name = valstr((f"Enter option {i+1} : "))
        importance = valint(("Importance: "))
        effort = valint(("Effort: "))
        urgency = valint(("urgency: "))
        reward = valint(("reward: "))
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
