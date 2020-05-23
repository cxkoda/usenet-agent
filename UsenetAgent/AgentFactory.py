from .HitnewsAgent import HitnewsAgent
from .UsenetFarmAgent import UsernetFarmAgent

def getUsenetAgent(host, *args, **kwargs):
    if host == "Hitnews":
        return HitnewsAgent(*args, **kwargs)
    elif host == "UsenetFarm":
        return UsernetFarmAgent(*args, **kwargs)
    else:
        raise Exception("Unknown Host, no Agent available")