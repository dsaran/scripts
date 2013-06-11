# This script starts up weblogic 10 managed servers.
# Version: $Id: start_ms.py 240 2010-03-22 13:20:34Z dsaran $

WEBLOGIC_USER='weblogic10'
WEBLOGIC_PASS='weblogic10'
WEBLOGIC_URL='t3://10.0.0.x:11001'
WEBLOGIC_DOMAIN_NAME='some_domain'
WEBLOGIC_DOMAIN_DIR='/opt/weblogic10/bea/domains/' + WEBLOGIC_DOMAIN_NAME

def read(label, default=''):
  print label + ": ",
  input = raw_input().strip()
  return input or default

def read_server():
    server = None
    servers = get('Servers')
    idx = 0
    print "Choose the server:"
    for s in servers:
        print str(idx) + ' - ' + s.getKeyProperty('Name')
        idx = idx + 1

    while true:
        try: 
            idx = read('Server [0]','0')
            server = servers[int(idx)].getKeyProperty('Name')
            break
        except (IndexError, ValueError):
            print "Invalid option, try again..."

    return server

def main():
    import sys
    args = sys.argv[1:]

    connect(WEBLOGIC_USER, WEBLOGIC_PASS, WEBLOGIC_URL)

    if args:
        start_ms(args[0])
    else:
        server_name = read_server()
        start_ms(server_name)

def start_ms(server_name):
    try:
        nmConnect(domainName=WEBLOGIC_DOMAIN_NAME, username=WEBLOGIC_USER, password=WEBLOGIC_PASS, domainDir=WEBLOGIC_DOMAIN_DIR)
    except:
        # Workaround for a bug with nmConnect on Weblogic 10 MP1
        nmConnect()

    start(server_name, 'Server')

if __name__ == 'main':
    main()

