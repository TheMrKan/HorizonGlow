
certfile = "certbot/conf/live/miami-cash.com/fullchain.pem"
keyfile = "certbot/conf/live/miami-cash.com/privkey.pem"
ca_certs = "certbot/conf/live/miami-cash.com/chain.pem"

bind = "0.0.0.0:443"

workers = 12

worker_class = "sync"

timeout = 30

accesslog = "-"
errorlog = "-"
loglevel = "debug"

secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
forwarded_allow_ips = '*'
