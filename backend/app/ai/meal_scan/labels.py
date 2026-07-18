CANONICAL_ALIASES={"roti":"chapati","phulka":"chapati","white_rice":"plain_rice","steamed_rice":"plain_rice","dal_tadka":"dal","yellow_dal":"dal","lentil_curry":"dal","vegetable_curry":"mixed_vegetable_curry","mixed_veg":"mixed_vegetable_curry","yogurt":"curd"}
COUNTABLE={"chapati","idli","boiled_egg","fried_egg","banana","dosa"}
def canonical_label(label:str)->str:
    normalized="_".join(label.lower().strip().replace("-"," ").split())
    return CANONICAL_ALIASES.get(normalized,normalized)
def display_label(label:str)->str:return label.replace("_"," ").title()
