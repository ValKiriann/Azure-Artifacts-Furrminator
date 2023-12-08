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

    sorted_versions_array = sorted(versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))
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

    stable_versions_to_keep = 10
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

    sorted_versions_array = sorted(versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))
    sorted_releases_array = sorted(release_versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))
    sorted_prereleases_array = sorted(prerelease_versions_array, reverse=True, key=lambda v: semver.VersionInfo.parse(v))

    # if state["verbose"]:
    #     console.print('[INFO]: Versions array:\n {}'.format(versions_array), style="info")
    #     rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")
    #     console.print('[INFO]: Releases array:\n {}'.format(sorted_releases_array), style="info")
    #     rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")
    #     console.print('[INFO]: Prereleases array:\n {}'.format(sorted_prereleases_array), style="info")

    instructions_message = ("The actual process contemplates to store last {} stable versions and last {} "
        "prerelease versions of the actual working release".format(stable_versions_to_keep,prerelease_versions_to_keep))
    console.print(instructions_message)

    release_versions_array_preserve = []
    prerelease_versions_array_preserve = []
    release_versions_array_delete = sorted_releases_array.copy()
    prerelease_versions_array_delete = sorted_prereleases_array.copy()

    if stable_versions_to_keep > len(sorted_releases_array):
        console.print('[WARN]: There are less stable releases than the minimum setted to be stored', style="warning")
        console.print('[WARN]: Number or stable releases {}, number of stable versions to keep {}'.format(len(sorted_releases_array), stable_versions_to_keep), style="warning")
        console.print('[WARN]: Skipping releases purge', style="warning")
        release_versions_array_preserve = sorted_releases_array.copy()
        release_versions_array_delete = []
    else:
        for i in range(stable_versions_to_keep):
            release_versions_array_preserve.append(sorted_releases_array[i])
            release_versions_array_delete.remove(sorted_releases_array[i])
        # if state["verbose"]:
            # print('Actual Stable versions', sorted_releases_array)
            # print('Stable versions to preserve', release_versions_array_preserve)
            # print('Stable versions to delete', release_versions_array_delete)
            # rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")
            # versions_preview_message = ""
            # for version in sorted_releases_array:
            #     if version in release_versions_array_preserve:
            #         versions_preview_message += version + " "
            #     elif version in release_versions_array_delete:
            #         versions_preview_message += "[red bold]" + version + "[/red bold] "
            #     else:
            #         versions_preview_message += "[orange bold]" + version + "[/orange bold] "
            # rprint("Please, confirm that the selected versions are ok. Versions in red will be deleted. If any version is in orange, furrminator does not know what to do with it")
            # rprint(versions_preview_message)

    last_prerelease_cleaned = re.sub('(-)(.*)', '', sorted_prereleases_array[0])
    for version in sorted_prereleases_array:
        if last_prerelease_cleaned in version:
            if len(prerelease_versions_array_preserve) < 10:
                prerelease_versions_array_preserve.append(version)
                prerelease_versions_array_delete.remove(version)
            else:
                break
    if state["verbose"]:
        # print('Actual Prerelease versions', sorted_prereleases_array)
        # print('Prerelease versions to preserve', prerelease_versions_array_preserve)
        # print('Prerelease versions to delete', prerelease_versions_array_delete)
        # rprint("[violet]♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ [violet]")
        versions_preview_message = ""
        versions_array_preserve = release_versions_array_preserve.copy() + prerelease_versions_array_preserve.copy()
        versions_array_delete = release_versions_array_delete.copy() + prerelease_versions_array_delete.copy()
        if len(versions_array_delete) > 0:
            for version in sorted_versions_array:
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
            

def exit(actual_response, state):
    console.print("Have a nice day!", style="info")
    raise typer.Exit()