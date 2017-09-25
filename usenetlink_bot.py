import os, platform
import string
import datetime, time
import requests
import imaplib
from configobj import ConfigObj
from usenetLIB import id_generator, name_dotter, raise_mail_step, set_bot_entry
import email
import asyncio
from proxybroker import Broker

async def use(proxies, proxy_dict):
    while True:
        proxy = await proxies.get()
        if proxy is None:
            break
        else:
            proxy_dict['http'] = ('%s:%s' % (proxy.host, proxy.port))

async def find(proxies, loop):
    broker = Broker(queue=proxies,
                    timeout=8,
                    attempts_conn=3,
                    max_concurrent_conn=200,
                    judges=['https://httpheader.net/', 'http://httpheader.net/'],
                    providers=['http://www.proxylists.net/'],
                    verify_ssl=False,
                    loop=loop)

    # only anonymous & high levels of anonymity for http protocol and high for others:
    types = ['HTTP']
    countries = ['US', 'GB', 'DE']
    limit = 4

    await broker.find(types=types, countries=countries, limit=limit)# countries=countries)


def usenetlink_bot():
    proxy_dict = {'http': '104.236.65.142:8080'}

    loop = asyncio.get_event_loop()
    proxies = asyncio.Queue(loop=loop)
    tasks = asyncio.gather(find(proxies, loop), use(proxies, proxy_dict))
    loop.run_until_complete(tasks)

    print(proxy_dict)

    cfgpath = "config.ini"
    sabname = 'usenetlinkBot'
    hostname = 'usenetlink'

    Config = ConfigObj(cfgpath)

    sabpath = os.getenv(Config['sabnzbd'][platform.system()]['start_dir'])+Config['sabnzbd'][platform.system()]['inipath']
    SabConfig = False
    if os.path.isfile(sabpath):
        SabConfig = ConfigObj(sabpath)

    #hitbot_log=open(Config['bot']['hitbot_log'],'a')
    #hitbot_log.write('\n'+datetime.datetime.strftime(datetime.datetime.now(), '%a %d-%m-%Y %H:%M:%S')+'\n')

    login=id_generator()
    passwd=''

    #br = mechanize.Browser()
    #br.set_handle_robots(False)
    #br.set_handle_equiv(False)
    #br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    #mail = name_dotter(Config['MAIL']['name'], int(Config[hostname]['dotting_step'])+3)+'@'+Config['MAIL']['domain']
    #login = id_generator()
    html_file = open('res.html', 'w+')


    #res = requests.post('http://members.usenetlink.com/signup/60minutes', data={'login': login, 'email': mail, 'product_id_page-0[]': "8-8", '_save_': "page-0", '_qf_page-0_next': "Next", 'paysys_id': "free"})

    #html_file.write(res.text)


    n = 0
    while True:
        n += 1
        print('Getting Trial')
        mail = name_dotter(Config['MAIL']['name'], int(Config[hostname]['dotting_step']))+\
               '+'+ login +\
               '@'+Config['MAIL']['domain']
        response = requests.post('http://members.usenetlink.com/signup/60minutes',
                            data={'login': login, 'email': mail, 'product_id_page-0[]': "8-8",
                                  '_save_': "page-0", '_qf_page-0_next': "Next", 'paysys_id': "free"},
                            proxies=proxy_dict)
        html_file.write(response.text)
        raise_mail_step(Config, hostname)
        if response.text.find('already exists') == -1:
            html_file.write(response.text)
            break
        if n > 15:
            raise RuntimeError

    html_file.close()

    #hitbot_log.write('\t- Connecting to IMAP...\t\t')
    imap = imaplib.IMAP4_SSL('imap.gmail.com',993)
    imap.login(Config['MAIL']['login_user'], Config['MAIL']['login_pass'])
    #hitbot_log.write('done\n')

    n = 0
    while True:
        n += 1
        print(n)
        if n > 15:
            raise RuntimeError

        print('\t- Waiting for activation mail...\t\t')
        #hitbot_log.write('\t- Waiting for mail...\t\t')
        time.sleep(1)
        #hitbot_log.write('done\n')
        imap.list()
        # Out: list of "folders" aka labels in gmail.
        imap.select("inbox") # connect to inbox.

        result, data = imap.uid('search', None, '(HEADER Subject "UsenetLink - Account Verification")') # search and return uids
        latest_email_uid = data[0].split()[-1]
        result, data = imap.uid('fetch', latest_email_uid, '(RFC822)')

        raw_email = data[0][1].decode('utf-8')
        email_message = email.message_from_string(raw_email)
        body = ''
        for part in email_message.walk():
            if part.get_content_type() == "text/plain": # ignore attachments/html
                body = body + part.get_payload(decode=True).decode('utf-8')
            else:
                continue

        link = body.split('\n')[4]

        if (link != Config[hostname]['activation_link']):
            Config[hostname]['activation_link'] = link
            break

    #hitbot_log.write('\t- Activation link found:\t'+link+'\n')
    requests.get(link, verify=False, proxies=proxy_dict)

    n = 0
    while True:
        n+=1
        if n > 15:
            raise RuntimeError
        print('\t- Waiting for information mail...\t\t')
        #hitbot_log.write('\t- Waiting for mail...\t\t')
        time.sleep(1)
        #hitbot_log.write('done\n')
        imap.list()
        # Out: list of "folders" aka labels in gmail.
        imap.select("inbox") # connect to inbox.

        result, data = imap.uid('search', None, '(HEADER Subject "UsenetLink - Membership Information")') # search and return uids
        latest_email_uid = data[0].split()[-1]
        result, data = imap.uid('fetch', latest_email_uid, '(RFC822)')

        raw_email = data[0][1].decode('utf-8')
        email_message = email.message_from_string(raw_email)
        body = ''
        for part in email_message.walk():
            if part.get_content_type() == "text/plain": # ignore attachments/html
                body = body + part.get_payload(decode=True).decode('utf-8')
            else:
                continue

        #link_begin = body.find('Your password:')
        #passwd = body[link_begin+15: link_begin+23]

        username = body.split('\n')[6][17:].strip()
        passwd = body.split('\n')[7][18:].strip()

        if (passwd != Config[hostname]['password']):
            #Config[hostname]['activation_link'] = passwd
            break





    #hitbot_log.write('\t- Writing config files...\t')
    set_bot_entry(SabConfig, Config, username, passwd, hostname, sabname)
    #hitbot_log.write('done\n')

    if (SabConfig != False):
        #hitbot_log.write('\t- Restarting sabnzbd...\t\t')
        SabRestart='http://localhost:8080/api?mode=restart&output=xml&apikey='+SabConfig['misc']['api_key']
        try:
            requests.get(SabRestart)
            #hitbot_log.write('done\n')
        except requests.exceptions.RequestException:
            #hitbot_log.write('failed\n')
            pass

    return 0

if __name__ == '__main__':
    usenetlink_bot()