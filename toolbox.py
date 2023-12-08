from distutils.version import LooseVersion
import semver
from semver.version import Version
import re
import typer
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

def create_versions_table_info(response_data, state):
    package_name = response_data['package_name']
    package_versions = response_data['data']
    versions_array = list()
    release_versions_array = list()
    prerelease_versions_array = list()


    for version in package_versions:
        versions_array.append(version['version'])
        if '-' in version['version']:
            prerelease_versions_array.append(version['version'])
        else:
            release_versions_array.append(version['version'])

    sorted_releases_array = sorted(release_versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))
    sorted_prereleases_array = sorted(prerelease_versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))
    
    table = Table("Property", "Description", show_lines=True)
    table.add_row("Name", package_name, style="on violet")
    table.add_row("Number of stored versions", str(len(package_versions)))
    table.add_row("Number of stored releases", str(len(sorted_releases_array)))
    table.add_row("Number of stored prereleases", str(len(sorted_prereleases_array)))
    table.add_row("Latest release", str(sorted_releases_array[0] if len(sorted_releases_array) > 0 else "None"))
    table.add_row("Latest prerelease", str(sorted_prereleases_array[0]) if len(sorted_prereleases_array) > 0 else "None")
    table.add_row("Oldest version", str(min(versions_array, key=Version.parse)))

    rprint(table)
    rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")

def generate_feed_list(response_object, state):
    feed_list = list()
    for feed in response_object['data']:
        feed_list.append({ 'name':feed['name'], 'value':feed['_links']['packages']['href'] })
    return feed_list

def predict_versions_to_clean(response_data, state):
    create_versions_table_info(response_data, state)

    stable_versions_to_keep = 5
    prerelease_versions_to_keep = 10

    package_versions = response_data['data']
    package_name = response_data['package_name']

    versions_array = list()
    release_versions_array = list()
    prerelease_versions_array = list()

    for version in package_versions:
        versions_array.append(version['version'])
        if '-' in version['version']:
            prerelease_versions_array.append(version['version'])
        else:
            release_versions_array.append(version['version'])
    
    sorted_releases_array = sorted(release_versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))
    sorted_prereleases_array = sorted(prerelease_versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))

    # if state["verbose"]:
    #     console.print('[INFO]: Versions array:\n {}'.format(versions_array), style="info")
    #     rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")
    #     console.print('[INFO]: Releases array:\n {}'.format(sorted_releases_array), style="info")
    #     rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")
    #     console.print('[INFO]: Prereleases array:\n {}'.format(sorted_prereleases_array), style="info")

    instructions_message = ("[INFO]: The actual process contemplates to store last {} stable versions and last {} "
        "prerelease versions of the actual working release".format(stable_versions_to_keep,prerelease_versions_to_keep))
    console.print(instructions_message, style="info")
    console.print("[INFO]: Based on this, Furrminator recommends you to delete:", style="info")

    last_prerelease_cleaned = re.sub('(-)(.*)', '', prerelease_versions_array[0])
    is_actual_release_stable = semver.compare(versions_array[0], last_prerelease_cleaned)
    if state["verbose"]:
        message = "[INFO] Actual release matches latest prerelease version" if is_actual_release_stable == 0 else "[INFO] Actual release is lower than latest prerelease version"
        console.print(message.format(versions_array), style="info")
    if is_actual_release_stable < 0:
        print('The actual release is lower than the latest prerelease. we recommend storing last 10 prerelease versions of')
        # TODO: count how many of latest prerelease are in the prerelease array
        # if more than 10, pop out first 10, leave the rest for the array to present for deletion
    elif is_actual_release_stable == 0:
        #TODO: pop out actual release and last 10 prerelease of this version
        # pop out next 4 release versions to avoid deletion
        count = 5 if len(versions_array) >= 5 else len(versions_array)
        versions_array_preserve = []
        versions_array_delete = sorted_releases_array.copy()
        for i in range(count):
            versions_array_preserve.append(sorted_releases_array[i])
            versions_array_delete.remove(sorted_releases_array[i])
        if state["verbose"]:
            print('stable versions array', sorted_releases_array)
            print('stable versions to preserve', versions_array_preserve)
            print('stable versions to delete', versions_array_delete)
            rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")

def exit(actual_response, state):
    console.print("Have a nice day!", style="info")
    raise typer.Exit()