import json

import optparse
parser = optparse.OptionParser()
parser.add_option(
        '-d', '--datasourceId',
        action='store', type='string', dest='datasourceId',
        help='DatasourceId.')

(options, args) = parser.parse_args()
dashboardId =options.datasourceId

with open('grafanastatuscode.json') as f:
    data = json.load(f)

for panel in data['panels']:
    panel['datasource']['uid'] = dashboardId
    panel['targets'][0]['datasource']['uid'] = dashboardId

with open('grafanastatuscode.json', 'w') as f:
    json.dump(data, f,indent=2)
