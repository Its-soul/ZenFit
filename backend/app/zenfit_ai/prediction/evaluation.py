def evaluate_binary(y_true:list[int], probabilities:list[float], minimum_samples:int=30)->dict:
    if len(y_true)<minimum_samples or len(set(y_true))<2: return {"status":"insufficient_data","sample_count":len(y_true),"minimum_samples":minimum_samples}
    from sklearn.metrics import accuracy_score,average_precision_score,brier_score_loss,f1_score,precision_score,recall_score,roc_auc_score
    predicted=[int(p>=.5) for p in probabilities]
    return {"status":"ok","sample_count":len(y_true),"roc_auc":roc_auc_score(y_true,probabilities),"pr_auc":average_precision_score(y_true,probabilities),"accuracy":accuracy_score(y_true,predicted),"precision":precision_score(y_true,predicted,zero_division=0),"recall":recall_score(y_true,predicted,zero_division=0),"f1":f1_score(y_true,predicted,zero_division=0),"brier_score":brier_score_loss(y_true,probabilities)}
