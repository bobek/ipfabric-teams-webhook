# IP Fabric Webhook Integration for Microsoft Teams

## Setup

### IP Fabric Setup

- Go to Settings > Webhooks > Add webhook
- Provide a name
- URL will be: 'http://\<YOUR IP/DNS\>:8000/ipfabric'
- Copy secret
- Select if you want both Snapshot and Intent Events

### Environment Setup

- Rename sample.env to .env
- Edit .env with your IPF and Teams variables
  - Default IP Fabric alerts can be found in [ipf_alerts.json](ipf_alerts.json) and then minified into IPF_ALERTS
  - Set IPF_VERIFY to False if your IP Fabric SSL cert is not trusted
  - IPF_SECRET is found in the webhook settings page
  - IPF_URL must be in the following format without any trailing information 'https://demo3.ipfabric.io/'
  - IPF_TOKEN is an API token created in Settings > API Token
  - TEAMS_URL is found when adding an "Incoming Webhook" on a Teams Channel
  - IPF_TEST will not send test alerts to the channel when set to False

## Running

### Python

- pip3 install -r requirements.txt
- cd src
- python3 api.py

### Docker

- docker compose up
