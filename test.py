target_views = 0
startingTarget_views = 1000
OldViewsPercentage = 10


for x in range(0,10):
    target_views = target_views + round(startingTarget_views * (OldViewsPercentage / 100))
    print(target_views)

def linkToID(lnk):
    res1 = lnk.replace('https://t.me/', '').split('/')
    res2 = res1[1].split('?')
    return int(res2[0])

#print(linkToID("https://t.me/testingchqnnel/12?single"))