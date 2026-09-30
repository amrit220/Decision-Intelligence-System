def process_data(factor_value_dict, weights):
    names =  list(factor_value_dict.keys())
    #print(factor_value_dict.items())
    #acess the dict for option and thier factors
    scores = {}
    for name, factors in factor_value_dict.items():
        score = 0 #reset to 0 per option
        #acess the nested dict for factors and thier value
        for factor, value in factors.items():
            weight = weights.get(factor,1)
            score += value*weight

        scores[name] = score
    return scores

def pick_best_option(scores):
    best = max(scores, key=scores.get)
    return best, scores[best] #returns the best option and the score



#Future upgrade for rankings. Need to study this lambda shit aswell
#def get_ranking(scores):
#    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
