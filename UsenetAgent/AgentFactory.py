from .HitnewsAgent import HitnewsAgent
from .UsenetFarmAgent import UsernetFarmAgent

def getUsenetAgent(host, *args, **kwargs):
    if host == "free.hitnews.com":
        return HitnewsAgent(*args, **kwargs)
    elif host == "news.usenet.farm":
        return UsernetFarmAgent(*args, **kwargs)
    else:
        raise Exception("Unknown Host, no Agent available")