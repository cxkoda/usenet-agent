import string
import random
import datetime




def id_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def name_dotter(name, step):
    return ''.join(name[i]+'.' if int(step/2**i)%2==1 else name[i] for i in range(len(name)))

def raise_mail_step(cfg, hostname):
    cfg[hostname]['dotting_step']=int(cfg[hostname]['dotting_step'])+1
    cfg.write()
    return True

def set_bot_entry(SABcfg, cfg, user, passwd, hostname, sabname):
    cfg[hostname]['username']=user
    cfg[hostname]['password']=passwd
    cfg[hostname]['generated']=datetime.datetime.strftime(datetime.datetime.now(), '%a %d-%m-%Y %H:%M:%S')
    cfg[hostname]['worked']=0
    cfg.write()
    if (SABcfg != False):
        try:
            SABcfg['servers'][sabname]['username']=user
            SABcfg['servers'][sabname]['password']=passwd
        except:
            dd=dict(cfg[hostname])
            #del dict['worked']
            SABcfg['servers'][sabname] = dd

        SABcfg.write()
    return

