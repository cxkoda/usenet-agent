from UsenetAgent.SabnzbdHandler import SabnzbdHandler

mockConfig = {
    'sabnzbd':
        {
            'address': '192.168.0.82',
            'port': '8080',
            'apikey': 'asdas',
            'ssl': False
        }
}

sab = SabnzbdHandler(mockConfig)
r = sab.addServer('test', 'testusername', 'testpassword')
