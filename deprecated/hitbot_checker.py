import os, platform
import nntplib as nntp
import time
import datetime
from configobj import ConfigObj
from usenetlink_bot import usenetlink_bot


def test_server(cfg, name):
    try:
        if cfg[name]['ssl'] == '1':
            nntp.NNTP_SSL(cfg[name]['host'], port=cfg[name]['port'], user=cfg[name]['username'], password=cfg[name]['password'])
        else:
            nntp.NNTP(cfg[name]['host'], port=cfg[name]['port'], user=cfg[name]['username'], password=cfg[name]['password'])
        cfg[name]['worked'] = 1
        cfg.write()
        return True
    except:
        return False

def sys_ping(adress):
    if platform.system()=='Linux':
        return os.system('ping -c 1 -W 1 '+ adress +' > /dev/null')
    if platform.system()=='Windows':
        return os.system('PING '+ adress +' -n 1 -w 1000 > NUL')
    else:
        return 1


def start_watchdog(hostname, Config, loop=True):

    #bot = {'hitnews': hitbot.hitbot, 'usenetlink': usenetlink_bot.usentlink_bot}[hostname]
    bot = {'usenetlink': usenetlink_bot}[hostname]


    if platform.system()=='Linux':
        os.system('clear')
    if platform.system()=='Windows':
        os.system('cls')




    while loop:

        Config.reload()

        checktime = datetime.datetime.now()
        checktimestr = datetime.datetime.strftime(checktime, '%a %d-%m-%Y %H:%M:%S')
        gentimestr = Config[hostname]['generated']
        gentime = datetime.datetime.strptime(gentimestr, '%a %d-%m-%Y %H:%M:%S')

        state = test_server(Config, hostname)

        if not state:
            time.sleep(5)
            state = test_server(Config, hostname)


        print('Last Generated Account: \t%s\n' % (gentimestr))
        print('Last Check:\t\t\t%s\n' % (checktimestr))

        if (sys_ping('www.google.com')!=0):
            print('No internet-connection!')
            time.sleep(10)
            continue

        print( 'Hitnews Worked: \t\t%s'%(Config[hostname]['worked']))
        print( 'Hitnews Connection: \t\t%s\n'%(str(state)))

        if state:
            Config['hitnews']['worked']=1
            Config.write()
            time.sleep(float(Config['bot']['check_intervall']))
        else:
            #if (Config[hostname]['worked']=='1' or (checktime - gentime).total_seconds()/3600. > 5.):
                print('Generating new account...')
                try:
                    bot()
                except:
                    pass
                Config.reload()
            #else:
            #    print('Waiting for account activation...')
            #    time.sleep(float(Config['bot']['check_intervall']))

        if platform.system()=='Linux':
            os.system('clear')
        if platform.system()=='Windows':
            os.system('cls')



if __name__ == '__main__':
    cfgfilepath = "config.ini"
    Config = ConfigObj(cfgfilepath)

    #start_watchdog('hitnews', Config)
    start_watchdog('usenetlink', Config)