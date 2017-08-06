import os, platform
import string
import datetime, time
import mechanize, requests
import imaplib
from configobj import ConfigObj
from usenetLIB import id_generator, name_dotter, raise_mail_step, set_bot_entry


def hitbot():
    cfgpath = "config.ini"
    sabname = 'HitBot'
    hostname = 'hitnews'

    Config = ConfigObj(cfgpath)

    sabpath = os.getenv(Config['sabnzbd'][platform.system()]['start_dir'])+Config['sabnzbd'][platform.system()]['inipath']
    SabConfig = False
    if os.path.isfile(sabpath):
        SabConfig = ConfigObj(sabpath)

    hitbot_log=open(Config['bot']['hitbot_log'],'a')
    hitbot_log.write('\n'+datetime.datetime.strftime(datetime.datetime.now(), '%a %d-%m-%Y %H:%M:%S')+'\n')

    hit_login=''
    hit_pass=''

    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.set_handle_equiv(False)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    while True:
        mail=name_dotter(Config['MAIL']['name'], int(Config[hostname]['dotting_step']))+'@'+Config['MAIL']['domain']
        hit_login=id_generator()
        hit_pass=id_generator()

        br.open("https://member.hitnews.com/signup.php")
        br.select_form(nr=0)
        hitbot_log.write('\t- Filling Form...\t\t')
        br['name_f'] = id_generator(10, string.ascii_lowercase)
        br['name_l'] = id_generator(10, string.ascii_lowercase)
        br['email'] = mail
        br['login'] = hit_login
        br['pass0'] = hit_pass
        br['pass1'] = hit_pass
        br.submit()
        hitbot_log.write('done\n')
        if [link.text for link in br.links()][3] == 'login':
            hitbot_log.write('\t- Email already used\n')
            raise_mail_step(Config, hostname)
        else:
            break

    br.select_form(nr=0)
    hitbot_log.write('\t- Agreeing to 2nd Form...\t')
    br.form.find_control('i_agree').items[0].selected=True
    br.submit()
    raise_mail_step(Config, hostname)
    hitbot_log.write('done\n')

    hitbot_log.write('\t- Connecting to IMAP...\t\t')
    imap = imaplib.IMAP4_SSL('imap.gmail.com',993)
    imap.login(Config['MAIL']['login_user'], Config['MAIL']['login_pass'])
    hitbot_log.write('done\n')

    while True:
        hitbot_log.write('\t- Waiting for mail...\t\t')
        time.sleep(10)
        hitbot_log.write('done\n')
        imap.list()
        # Out: list of "folders" aka labels in gmail.
        imap.select("inbox") # connect to inbox.

        result, data = imap.uid('search', None, '(HEADER Subject "Hitnews.com - Account Activation")') # search and return uids
        latest_email_uid = data[0].split()[-1]
        result, data = imap.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        link_begin=raw_email.find('http://member.hitnews.com/signup.php?cs=')
        link=raw_email[link_begin:link_begin+60]
        if (link != Config[hostname]['activation_link']):
            Config[hostname]['activation_link'] = link
            break

    hitbot_log.write('\t- Activation link found:\t'+link+'\n')
    br.open(link)

    hitbot_log.write('\t- Writing config files...\t')
    set_bot_entry(SabConfig, Config, hit_login, hit_pass, hostname, sabname)
    hitbot_log.write('done\n')

    if (SabConfig != False):
        hitbot_log.write('\t- Restarting sabnzbd...\t\t')
        SabRestart='http://localhost:8080/api?mode=restart&output=xml&apikey='+SabConfig['misc']['api_key']
        try:
            requests.get(SabRestart)
            hitbot_log.write('done\n')
        except requests.exceptions.RequestException:
            hitbot_log.write('failed\n')

    return 0

if __name__ == '__main__':
    hitbot()