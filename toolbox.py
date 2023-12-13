from distutils.version import LooseVersion
import semver
from semver.version import Version
import re
import typer
from dotenv import load_dotenv
import os
from rich import print as rprint
from rich.table import Table
from rich.console import Console
from rich.theme import Theme
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red"
})
console = Console(theme=custom_theme)

load_dotenv()
ORGANIZATION = os.getenv('ORGANIZATION')
STABLE_VERSIONS_TO_KEEP = int(os.getenv('STABLE_VERSIONS_TO_KEEP'))
PRERELEASE_VERSIONS_TO_KEEP = int(os.getenv('PRERELEASE_VERSIONS_TO_KEEP'))

def asciiLogo():
    return """
    ───────────────────────────────────────
    ───▐▀▄───────▄▀▌───▄▄▄▄▄▄▄─────────────
    ───▌▒▒▀▄▄▄▄▄▀▒▒▐▄▀▀▒██▒██▒▀▀▄──────────
    ──▐▒▒▒▒▀▒▀▒▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▀▄────────
    ──▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▄▒▒▒▒▒▒▒▒▒▒▒▒▀▄──────
    ▀█▒▒▒█▌▒▒█▒▒▐█▒▒▒▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌─────
    ▀▌▒▒▒▒▒▒▀▒▀▒▒▒▒▒▒▀▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐───▄▄
    ▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌▄█▒█
    ▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒█▀─
    ▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▀───
    ▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌────
    ─▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐─────
    ─▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▌─────
    ──▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐──────
    ──▐▄▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▄▌──────
    ────▀▄▄▀▀▀▀▀▄▄▀▀▀▀▀▀▀▄▄▀▀▀▀▀▄▄▀────────
    """

def createTableInfo(response_data, state):
    table = Table("Property", "Value", show_lines=True)
    for item in response_data['data']:
        table.add_row("Name", item['name'], style="on violet")
        table.add_row("ID", item['id'])
        table.add_row("Url", item['url'])

    rprint(table)
    rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")

'''
@function create_versions_table_info
@param {dictionary} package - dictionary that contains details related to tha package - see sanitize_package_info for structure
@param {dictionary} versions - dictionary that contains versions related to the package - see obtain_versions_from_package for structure
@param {dictionary} state - Object that contains the state of the tool
@description    This function creates an informational table related to the package selected and its versions
'''
def create_versions_table_info(package, versions):

    package_name = package['package_name']
    package_type = package['package_type']
    versions_array = versions['versions_array']
    release_versions_array = versions['release_versions_array']
    prerelease_versions_array = versions['prerelease_versions_array']
    
    table = Table("Property", "Description", show_lines=True)
    table.add_row("Name", package_name, style="on violet")
    table.add_row("Type", package_type)
    table.add_row("Number of stored versions", str(len(versions_array)))
    table.add_row("Number of stored releases", str(len(release_versions_array)))
    table.add_row("Number of stored prereleases", str(len(prerelease_versions_array)))
    table.add_row("Latest release", str(release_versions_array[0] if len(release_versions_array) > 0 else "None"))
    table.add_row("Latest prerelease", str(prerelease_versions_array[0]) if len(prerelease_versions_array) > 0 else "None")
    table.add_row("Oldest version", str(min(versions_array, key=Version.parse)))

    rprint(table)
    rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")

def generate_feed_list(response_data, state):
    feed_list = list()
    for feed in response_data['data']:
        feed_info = sanitize_feed_info(feed, state)
        feed_list.append({ 'name':feed['name'], 'value':feed_info })
    return feed_list

def sanitize_feed_info(feed, state):
    feed_info = {
        'feed_name': feed['name'],
        'feed_id': feed['id'],
        'feed_url': feed['_links']['packages']['href']
    }
    
    if state["verbose"]:
        console.print("[INFO]: Checking if this feed has a project", style="info")

    if 'project' in feed.keys():
        if state["verbose"]:
            console.print("[INFO]: Found project in feed, saving details", style="info")
        feed_info['project_name'] = feed['project']['name']
        feed_info['project_id'] = feed['project']['id']
    
    return feed_info

'''
@function sanitize_package_info
@param {dictionary} package - Dictionary that contains the raw info of a package
@param {dictionary} state - Object that contains the state of the tool
@description    This function sanitize the package info into the object used across the tool
'''
def sanitize_package_info(package, state):
    package_info = {
        'package_name': package['name'],
        'package_id': package['id'],
        'package_versions_url': package['_links']['versions']['href'],
        'package_type': package['protocolType']
    }
    if package['protocolType'] == 'maven':
        group_id = package['name'].split(sep=':')
        package_info['group_id'] = group_id[0]
        package_info['artifact_name'] = group_id[1]
    # if package['protocolType'] == 'Npm':
    #     if '/'in package['name']:
    #         scope = package['name'].split(sep='/')
    #         package_info['scope'] = scope[0]
    #         package_info['artifact_name'] = scope[1]
    return package_info

'''
@function obtain_versions_from_package
@param {dictionary} response_data - The last raw response from an api call
    response_data {
        data: {... last raw api response ...},
        continue: Bool, to control wheter to continue the flow or exit,
        feed: {... details of the selected feed...} see sanitize_feed_info,
        package: {... details of the selected package...} see sanitize_package_info,
    }
@param {dictionary} state - Object that contains the state of the tool
@description    This function creates sanitized version lists based on the versions that a package has
                It loops through the raw data response of the get_versions api function, 
                checks that the version was not deleted and, classifies it between stable or prerelease
'''
def obtain_versions_from_package(response_data, state):
    package = response_data['package']
    package_versions = response_data['data']
    versions_array = list()
    release_versions_array = list()
    prerelease_versions_array = list()

    for version in package_versions:
        if not 'isDeleted' in version:
            versions_array.append(version['version'])
            if '-' in version['version']:
                prerelease_versions_array.append(version['version'])
            else:
                release_versions_array.append(version['version'])

    sorted_versions_array = sorted(versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))
    sorted_releases_array = sorted(release_versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))
    sorted_prereleases_array = sorted(prerelease_versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))

    versions = {
        'versions_array': sorted_versions_array,
        'release_versions_array': sorted_releases_array, 
        'prerelease_versions_array': sorted_prereleases_array
    }

    if state["verbose"]:
        console.print('[INFO]: Versions array:\n {}'.format(sorted_versions_array), style="info")
        rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")
        console.print('[INFO]: Releases array:\n {}'.format(sorted_releases_array), style="info")
        rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")
        console.print('[INFO]: Prereleases array:\n {}'.format(sorted_prereleases_array), style="info")

    versions['prediction'] = predict_deletion(package, versions, state)

    return versions

def predict_deletion(package, versions, state):
    package_name = package['package_name']
    versions_array = versions['versions_array']
    release_versions_array = versions['release_versions_array']
    prerelease_versions_array = versions['prerelease_versions_array']

    instructions_message = ("The actual process contemplates to store last {} stable versions and last {} "
        "prerelease versions of the actual working release".format(STABLE_VERSIONS_TO_KEEP,PRERELEASE_VERSIONS_TO_KEEP))
    console.print(instructions_message)

    release_versions_array_preserve = []
    prerelease_versions_array_preserve = []
    release_versions_array_delete = release_versions_array.copy()
    prerelease_versions_array_delete = prerelease_versions_array.copy()

    if STABLE_VERSIONS_TO_KEEP > len(release_versions_array):
        if state['verbose']:
            console.print('[WARN]: There are less stable releases than the minimum setted to be stored', style="warning")
            console.print('[WARN]: Number or stable releases {}, number of stable versions to keep {}'.format(len(release_versions_array), STABLE_VERSIONS_TO_KEEP), style="warning")
            console.print('[WARN]: Skipping releases purge', style="warning")
        release_versions_array_preserve = release_versions_array.copy()
        release_versions_array_delete = []
    else:
        for i in range(STABLE_VERSIONS_TO_KEEP):
            release_versions_array_preserve.append(release_versions_array[i])
            release_versions_array_delete.remove(release_versions_array[i])

    if len(prerelease_versions_array) == 0:
        console.print('[WARN]: There are no prereleases for the package {}'.format(package_name), style="warning")
        console.print('[WARN]: Skipping pre-releases purge', style="warning")
    else:
        last_prerelease_cleaned = re.sub('(-)(.*)', '', prerelease_versions_array[0])
        for version in prerelease_versions_array:
            if last_prerelease_cleaned in version:
                if len(prerelease_versions_array_preserve) < PRERELEASE_VERSIONS_TO_KEEP:
                    prerelease_versions_array_preserve.append(version)
                    prerelease_versions_array_delete.remove(version)
                else:
                    break
    versions_array_preserve = release_versions_array_preserve.copy() + prerelease_versions_array_preserve.copy()
    versions_array_delete = release_versions_array_delete.copy() + prerelease_versions_array_delete.copy()
    
    prediction = {
        'versions_array_preserve': versions_array_preserve,
        'versions_array_delete': versions_array_delete
    }

    return prediction

def predict_versions_to_clean(response_data, state):
    package_name = response_data['package']['package_name']

    versions = response_data['versions']
    versions_array = versions['versions_array']
    release_versions_array = versions['release_versions_array']
    prerelease_versions_array = versions['prerelease_versions_array']

    instructions_message = ("The actual process contemplates to store last {} stable versions and last {} "
        "prerelease versions of the actual working release".format(STABLE_VERSIONS_TO_KEEP,PRERELEASE_VERSIONS_TO_KEEP))
    console.print(instructions_message)

    release_versions_array_preserve = []
    prerelease_versions_array_preserve = []
    release_versions_array_delete = release_versions_array.copy()
    prerelease_versions_array_delete = prerelease_versions_array.copy()

    if STABLE_VERSIONS_TO_KEEP > len(release_versions_array):
        console.print('[WARN]: There are less stable releases than the minimum setted to be stored', style="warning")
        console.print('[WARN]: Number or stable releases {}, number of stable versions to keep {}'.format(len(release_versions_array), STABLE_VERSIONS_TO_KEEP), style="warning")
        console.print('[WARN]: Skipping releases purge', style="warning")
        release_versions_array_preserve = release_versions_array.copy()
        release_versions_array_delete = []
    else:
        for i in range(STABLE_VERSIONS_TO_KEEP):
            release_versions_array_preserve.append(release_versions_array[i])
            release_versions_array_delete.remove(release_versions_array[i])

    if len(prerelease_versions_array) == 0:
        console.print('[WARN]: There are no prereleases for the package {}'.format(package_name), style="warning")
        console.print('[WARN]: Skipping pre-releases purge', style="warning")
    else:
        last_prerelease_cleaned = re.sub('(-)(.*)', '', prerelease_versions_array[0])
        for version in prerelease_versions_array:
            if last_prerelease_cleaned in version:
                if len(prerelease_versions_array_preserve) < PRERELEASE_VERSIONS_TO_KEEP:
                    prerelease_versions_array_preserve.append(version)
                    prerelease_versions_array_delete.remove(version)
                else:
                    break
    versions_preview_message = ""
    versions_array_preserve = release_versions_array_preserve.copy() + prerelease_versions_array_preserve.copy()
    versions_array_delete = release_versions_array_delete.copy() + prerelease_versions_array_delete.copy()
    if len(versions_array_delete) > 0:
        for version in versions_array:
            if version in versions_array_preserve:
                versions_preview_message += "[cyan bold]" + version + "[/cyan bold] "
            elif version in versions_array_delete:
                versions_preview_message += "[red bold]" + version + "[/red bold] "
            else:
                versions_preview_message += "[orange bold]" + version + "[/orange bold] "
        print("Based on this, Furrminator recommends you to delete:")
        rprint(versions_preview_message)
        rprint("Please, confirm that the selected versions are ok. Versions in [red bold]red[/red bold] will be deleted. If any version is in [orange bold]orange[/orange bold], furrminator does not know what to do with it")
    else:
        rprint("Based on this, there are no versions that meet the criteria of deletion")
        raise typer.Exit()
    
    response_data['package']['versions_array'] = versions_array
    response_data['package']['versions_array_preserve'] = versions_array_preserve
    response_data['package']['versions_array_delete'] = versions_array_delete
    return response_data

def exit(response_data, state):
    console.print("Have a nice day!", style="info")
    raise typer.Exit()