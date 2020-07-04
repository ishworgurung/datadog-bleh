#!/usr/bin/env python

# Datadog Monitor muter

from datadog import initialize, api
from datetime import timedelta, datetime

if __name__ == "__main__":
    MUTE_FOR = timedelta(days=1, hours=12)  # adjust
    MONITORS_PER_PAGE = 60

    options = {
        'api_key': '1234',
        'app_key': '1234'
    }

    initialize(**options)

    mute_monitor_ids = []
    # Get number of monitors (thus only single page)
    all_monitors = api.Monitor.search(per_page=1)

    total_monitor_count = all_monitors['metadata']['total_count']
    per_page = MONITORS_PER_PAGE
    num_iter = int(int(total_monitor_count) / int(MONITORS_PER_PAGE)) + 1 # last page

    # Get all monitors with name that starts with '(dev)'.
    for p in range(num_iter):
        paginated_monitors = api.Monitor.search(page=p, per_page=MONITORS_PER_PAGE)
        for e in paginated_monitors['monitors']:
            if e['name'].startswith("(dev)"):
                mute_monitor_ids.append({
                    'name': e['name'],
                    'id': int(e['id'])
                })

    monitor_ttl = int((datetime.now() + MUTE_FOR).timestamp())
    print(f"muting monitor POSIX timestamp: {monitor_ttl} (check https://www.epochconverter.com)")

    # Mute all monitors with name that starts with '(dev)'
    for mon in mute_monitor_ids:
        print(f"muting monitor name: {mon['name']} and id: {mon['id']} for 1d 12h")
        if mon['id'] != 0:
            response = api.Monitor.mute(mon['id'], end=monitor_ttl)
            if "errors" in response.keys():
                print(f"error occurred while muting monitor id: {mon['id']}")
                print(f"error: {response['errors']}")
