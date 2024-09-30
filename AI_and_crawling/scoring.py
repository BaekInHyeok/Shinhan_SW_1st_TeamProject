import json
from math import exp

# with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/label_descriptions.json") as f:
#     names_match = json.load(f)

# print(f"{names_match['attributes'][295]['name']}(295)")
# for i, attr in enumerate(names_match['attributes']):
#     if i != attr['id']:print(attr['id'])

# print(names_match['attributes'][235])

# d = {'0':12, '4':1, '3':2}
# d = sorted(d.items(), key= lambda x:int(x[0]))
# print(dict(d))
# print(len(d))

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/recm_weights.json") as f:
    weights = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/recm_weights_for.json") as f:
    weights_for = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/recm_weights_for_for.json") as f:
    weights_for_for = json.load(f)



with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/1hoodie.json") as f:
    hoodie = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/1top.json") as f:
    top = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/1tshirt.json") as f:
    tshirt = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/1crop.json") as f:
    crop = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/1croptop.json") as f:
    croptop = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/1slsstop.json") as f:
    slsstop = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/1slsstop2.json") as f:
    slsstop2 = json.load(f)



with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/4blazer.json") as f:
    blazer = json.load(f)



with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/6jean1.json") as f:
    jean = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/6leggings.json") as f:
    leggings = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/6pants.json") as f:
    pants = json.load(f)

with open("C:/closed/test/imaterialist-fashion-2020-fgvc7/prod_info/6slacks.json") as f:
    slacks = json.load(f)

def scoring_two_parts(part1, part2, fix="part1", coeff=10) :
    score_list = []

    if fix == "part1" :
        not_fixed = part2
    elif fix == "part2":
        not_fixed = part1

    for not_f in not_fixed :
        score = 0
        count = 0
        for cls in part1.keys():
            for attr in part1[cls]:
                for cls_ in not_f.keys():
                    if cls_ in weights[cls][str(attr)].keys():
                        for attr_ in not_f[cls_]:
                            cls_score = (weights_for[cls][str(attr)][cls_]+weights_for[cls_][str(attr_)][cls])/(weights_for_for[cls][str(attr)]+weights_for_for[cls_][str(attr_)])
                            score += (1/(1-cls_score))*((weights[cls][str(attr)][cls_][str(attr_)]*2)/(weights_for[cls][str(attr)][cls_]+weights_for[cls_][str(attr_)][cls]))
                            count += 1

        score /= count
        score_list.append(int(1000*(1-exp(-coeff*score))))

    return score_list

tops = [hoodie, top, tshirt, crop, croptop, slsstop, slsstop2]
tops_names = ["hoodie", "top", "tshirt", "crop", "croptop", "slsstop", "slsstop2"]
bottoms = [pants, jean, leggings, slacks]
bottoms_names = ["pants", "jean", "leggings", "slacks"]

for t, name in zip(tops, tops_names):
    print(bottoms_names)    
    print(name, scoring_two_parts(part1=t, part2=bottoms))
    print()

print(tops_names)
print("blazer", scoring_two_parts(part1=blazer, part2=tops))
print()
print(bottoms_names)
print("blazer", scoring_two_parts(part1=blazer, part2=bottoms))