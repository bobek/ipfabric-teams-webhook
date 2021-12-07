import pymsteams
from config import settings
from models import Event
from urllib.parse import urljoin
from pydantic.dataclasses import dataclass
from ipfabric import IPFClient
import logging

logger = logging.getLogger()


SNAP_URL = 'snapshot-management/'
IMAGE_URL = 'https://ipfabric.atlassian.net/wiki/download/attachments/13369347/ND?version=1&amp;' \
            'modificationDate=1527757876293&amp;cacheVersion=1&amp;api=v2'


@dataclass
class Link:
    text: str
    url: str


def file_download(event: Event):
    ipf = IPFClient(settings.ipf_url, token=settings.ipf_token)
    res = ipf.post('jobs/read', json=dict(force=True))
    res.raise_for_status()
    for job in res.json():
        if job["downloadFile"] and job["status"] == 'done' and job["snapshot"] == event.snapshot.id:
            return urljoin(settings.ipf_url, 'jobs/' + job["id"] + '/download')


def snapshot(event: Event):
    if event.status == 'completed':
        if event.action == 'clone':
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.clone_id)
            return Link('Snapshot Cloned', url)
        elif event.action == 'download':
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.file)
            return Link('Download Snapshot File', url)
        elif event.action == 'load':
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.id)
            return Link('Snapshot Loaded', url)
        elif event.action == 'unload':
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.id)
            return Link('Snapshot Unloaded', url)
        elif event.action == 'delete':
            url = urljoin(settings.ipf_url, SNAP_URL)
            return Link('Snapshot Deleted', url)
        elif event.action == 'discover':
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.id)
            return Link('Discovery Completed', url)
    else:
        if event.snapshot and event.snapshot.id:
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.id)
        else:
            url = urljoin(settings.ipf_url, SNAP_URL)
        return Link('Snapshot Management', url)


def add_link(message: pymsteams.connectorcard, event: Event):
    if event.type == 'snapshot':
        title = 'Snapshot: ' + event.action.capitalize() + ' - ' + event.status.capitalize()
        link = snapshot(event)
        message.addLinkButton(link.text, link.url)

    else:
        title = 'Intent Verification: ' + event.action.capitalize() + ' - ' + event.status.capitalize()
        message.addLinkButton("Snapshot Management", urljoin(settings.ipf_url, SNAP_URL + event.snapshot_id))
    return title


def add_facts(section: pymsteams.cardsection, event: Event):
    section.addFact("Requester", event.requester)
    section.addFact("Time", event.timestamp.strftime("%c"))
    if event.snapshot:
        section.addFact("Snapshot ID", event.snapshot.id)
        if event.snapshot.clone_id:
            section.addFact("Cloned ID", event.snapshot.clone_id)
        if event.snapshot.name:
            section.addFact("Snapshot Name", event.snapshot.name)
    if event.snapshot_id:
        section.addFact("Snapshot ID", event.snapshot_id)
    if event.test:
        section.addFact("Test", "True")


def add_snapshot_facts(snapshot_id: str):
    section = pymsteams.cardsection()
    ipf = IPFClient(settings.ipf_url, token=settings.ipf_token, snapshot_id=snapshot_id, verify=settings.ipf_verify)
    snap = ipf.snapshots[snapshot_id]
    section.addFact("Device Count", snap.count)
    section.addFact("Site Count", len(snap.sites))
    section.addFact("Start Time", snap.start.strftime("%c"))
    section.addFact("End Time", snap.end.strftime("%c"))
    section.addFact("Version", snap.version)
    for error in snap.errors:
        section.addFact(error.error_type, error.count)
    return section


def send_card(event: Event):
    if not settings.ipf_alerts.check_event(event) or (event.test and not settings.ipf_test):
        return
    message = pymsteams.connectorcard(settings.teams_url)
    message.color("01214A")
    message.summary("IP Fabric Event")
    title = add_link(message, event)
    message.title(title)
    section = pymsteams.cardsection()
    section.activityImage(IMAGE_URL)
    add_facts(section, event)
    message.addSection(section)

    if event.type == 'snapshot' and event.status == 'completed' and event.action in ['discover', 'load'] and \
            not event.test:
        try:
            message.addSection(add_snapshot_facts(event.snapshot.id))
        except:
            logger.error('Could not retrieve Snapshot information.')
    message.send()
