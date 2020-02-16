from .HitnewsAgent import HitnewsAgent

def getUsenetAgent(host, *args, **kwargs):
    if host == "free.hitnews.com":
        return HitnewsAgent(*args, **kwargs)
    else:
        return None