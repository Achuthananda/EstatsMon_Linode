"""Application exporter"""
#https://trstringer.com/quick-and-easy-prometheus-exporter/
#https://medium.com/aeturnuminc/configure-prometheus-and-grafana-in-dockers-ff2a2b51aa1d
'''
docker run -d --name prometheus -p 9090:9090 -v /Users/apadmana/Achuth/code_base/AkamaiInteralGit/CustomerCode/India/GrafanaPOC/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus --config.file=/etc/prometheus/prometheus.yml
docker run -d --name grafana -p 3000:3000 grafana/grafana
'''

#https://techdocs.akamai.com/edge-diagnostics/reference/post-estats

import os
import time
from prometheus_client import start_http_server, Gauge, Enum
import requests
import random,json
import configparser
from akamaihttp import AkamaiHTTPHandler

config = configparser.ConfigParser()
import os
cwd = os.path.dirname(os.path.abspath(__file__))
initfile = os.path.join(cwd, 'exportersettings')


config = configparser.ConfigParser()
config.read(initfile)

def geteStatsData():

    akhttp = AkamaiHTTPHandler(config['Akamai']['edgerclocation'])

    data = {}
    data['cpCode'] = config['Akamai']['cpcode']
    data['delivery'] = config['Akamai']['deliverynetwork']
    json_data = json.dumps(data)


    ep = '/edge-diagnostics/v1/estats'
    params = {}
    if config['Akamai']['accountSwitchKey'] != '':
        params['accountSwitchKey'] = config['Akamai']['accountSwitchKey']
    
    headers = {'Content-Type': 'application/json','Accept':'application/json'}

    result = akhttp.postResult(ep,json_data,headers,params)
    body = result[1]

    resp_body = {}

    origin_resp_body = {}
    origin_resp_body['1xx'] = 0.0
    origin_resp_body['2xx'] = 0.0
    origin_resp_body['3xx'] = 0.0
    origin_resp_body['4xx'] = 0.0
    origin_resp_body['5xx'] = 0.0

    edge_resp_body = {}
    edge_resp_body['1xx'] = 0.0
    edge_resp_body['2xx'] = 0.0
    edge_resp_body['3xx'] = 0.0
    edge_resp_body['4xx'] = 0.0
    edge_resp_body['5xx'] = 0.0

    #print(json.dumps(body,indent=2))
    if result[0] == 200:
        for i in body['result']['originStatusCodeDistribution']:
            if i['httpStatus'] in range(100,200):
                origin_resp_body['1xx'] = round(origin_resp_body['1xx'] + i['percentage'],2)
            elif i['httpStatus'] in range(200,300):
                origin_resp_body['2xx'] = round(origin_resp_body['2xx'] + i['percentage'],2)
            elif i['httpStatus'] in range(300,400):
                origin_resp_body['3xx'] = round(origin_resp_body['3xx'] + i['percentage'],2)
            elif i['httpStatus'] in range(400,500):
                origin_resp_body['4xx'] = round(origin_resp_body['4xx'] + i['percentage'],2)
            elif i['httpStatus'] in range(500,600):
                origin_resp_body['5xx'] = round(origin_resp_body['5xx'] + i['percentage'],2)


        for i in body['result']['edgeStatusCodeDistribution']:
            if i['httpStatus'] in range(100,200):
                edge_resp_body['1xx'] = round(edge_resp_body['1xx'] + i['percentage'],2)
            elif i['httpStatus'] in range(200,300):
                edge_resp_body['2xx'] = round(edge_resp_body['2xx'] + i['percentage'],2)
            elif i['httpStatus'] in range(300,400):
                edge_resp_body['3xx'] = round(edge_resp_body['3xx'] + i['percentage'],2)
            elif i['httpStatus'] in range(400,500):
                edge_resp_body['4xx'] = round(edge_resp_body['4xx'] + i['percentage'],2)
            elif i['httpStatus'] in range(500,600):
                edge_resp_body['5xx'] = round(edge_resp_body['5xx'] + i['percentage'],2)

    resp_body['edge'] = edge_resp_body
    resp_body['origin'] = origin_resp_body  
    return resp_body


class AppMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, polling_interval_seconds=5):
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        self.origin_1xx = Gauge("origin_1xx", "Origin 1xx")
        self.origin_2xx = Gauge("origin_2xx", "Origin 2xx")
        self.origin_3xx = Gauge("origin_3xx", "Origin 3xx")
        self.origin_4xx = Gauge("origin_4xx", "Origin 4xx")
        self.origin_5xx = Gauge("origin_5xx", "Origin 5xx")

        self.edge_1xx = Gauge("edge_1xx", "Edge 1xx")
        self.edge_2xx = Gauge("edge_2xx", "Edge 2xx")
        self.edge_3xx = Gauge("edge_3xx", "Edge 3xx")
        self.edge_4xx = Gauge("edge_4xx", "Edge 4xx")
        self.edge_5xx = Gauge("edge_5xx", "Edge 5xx")

    def run_metrics_loop(self):
        """Metrics fetching loop"""
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)


    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        resp_body = geteStatsData()
        
        # Update Prometheus metrics with application metrics

        self.origin_1xx.set(resp_body['origin']['1xx'])
        self.origin_2xx.set(resp_body['origin']['2xx'])
        self.origin_3xx.set(resp_body['origin']['3xx'])
        self.origin_4xx.set(resp_body['origin']['4xx'])
        self.origin_5xx.set(resp_body['origin']['5xx'])

        self.edge_1xx.set(resp_body['edge']['1xx'])
        self.edge_2xx.set(resp_body['edge']['2xx'])
        self.edge_3xx.set(resp_body['edge']['3xx'])
        self.edge_4xx.set(resp_body['edge']['4xx'])
        self.edge_5xx.set(resp_body['edge']['5xx'])

def main():
    """Main entry point"""
    polling_interval_seconds = int( config.get('Exporter', 'polling_interval'))
    exporter_port = int( config.get('Exporter', 'exporter_port') )

    app_metrics = AppMetrics(polling_interval_seconds=polling_interval_seconds)
    start_http_server(exporter_port)
    print('HTTP Exporter Server is Running on Port {}'.format(exporter_port))
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
