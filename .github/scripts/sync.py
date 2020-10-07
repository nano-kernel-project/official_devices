import sys
import json
import github

newjson = {}
username = os.environ['GH_USERNAME']
password = os.environ['GH_PASSWORD']
auth = Github(username, password)
repo = auth.get_repo('PixysOS/official_devices')

try:
    devices = json.loads(open('devices.json', 'r').read())
except:
    print('devices.json has a invalid format')
    sys.exit(1)

try:
    teams = json.loads(open('teams.json', 'r').read())
except:
    print('teams.json has a invalid format')
    sys.exit(1)


try:
    bases = json.loads(open('bases.json', 'r').read())
except:
    print('versions.json has a invalid format')
    sys.exit(1)

for base in bases.keys():
    newjson[base] = []
    for device in devices:
        if not {'brand', 'name', 'codename', 'supported_bases'} <= set(device.keys()):
            print(
                f"Skipped device entry @ index {devices.index(device)} for insufficient keys.")
            continue
        newdevice = {}
        newdevice['brand'] = device['brand']
        newdevice['name'] = device['name']
        newdevice['codename'] = device['codename']
        for supported_base in device['supported_bases']:
            if supported_base['name'] != base:
                continue
            newdevice['xda_thread'] = supported_base['xda_thread'] if supported_base.get(
                'xda_thread') else ''
            maintainers_name = []
            maintainers_github = []
            for team in teams:
                if not {'full_name', 'github_username', 'devices'} <= set(team.keys()):
                    print(
                        f"Skipped team entry @ device index {devices.index(device)} and team index {teams.index(team)} for insufficient keys.")
                    continue
                for tdevice in team['devices']:
                    if tdevice['codename'] != device['codename'] or base not in tdevice['bases']:
                        continue
                    maintainers_name.append(team['full_name'])
                    maintainers_github.append(team['github_username'])
            newdevice['maintainers_name'] = ', '.join(maintainers_name)
            newdevice['maintainers_github'] = ', '.join(maintainers_github)
            newjson[base].append(newdevice)
            break

for base in newjson:
    content = json.dumps(newjson[base], indent=3, sort_keys=False)
    file = repo.get_contents("devices.json", ref=f"{base}")
    repo.update_file(file.path, f"Sync master commit {os.environ['GITHUB_SHA']}", f"{content}", file.sha, branch=f"{base}")
