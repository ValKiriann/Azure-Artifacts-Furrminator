import typer
from dotenv import load_dotenv
import os
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
'''
@function generate_delete_url
@param {dictionary} package - {... details of the selected package...} see sanitize_package_info
@param {dictionary} feed -  {... details of the selected feed...} see sanitize_feed_info
@param {float} version - the version of the package
@param {dictionary} state - Object that contains the state of the tool
@description    This function generates the url to call Azure API to delete a package by version
'''
def generate_delete_url(package, feed, version, state):
    url = ""
    if package['package_type'] == 'maven':
        url = 'https://pkgs.dev.azure.com/{}/{}/_apis/packaging/feeds/{}/maven/groups/{}/artifacts/{}/versions/{}'.format(ORGANIZATION, feed['project_id'], feed['feed_id'], package['group_id'], package['artifact_name'], version)
    elif package['package_type'] == 'Npm':
        if 'project_id' in feed:
            url = 'https://pkgs.dev.azure.com/{}/{}/_apis/packaging/feeds/{}/npm/{}/versions/{}'.format(ORGANIZATION, feed['project_id'], feed['feed_id'], package['package_name'], version)
        else:
            url = 'https://pkgs.dev.azure.com/{}/_apis/packaging/feeds/{}/npm/{}/versions/{}'.format(ORGANIZATION, feed['feed_id'], package['package_name'], version)
    elif package['package_type'] == 'UPack':
        if 'project_id' in feed:
            url = 'https://pkgs.dev.azure.com/{}/{}/_apis/packaging/feeds/{}/upack/packages/{}/versions/{}'.format(ORGANIZATION, feed['project_id'], feed['feed_id'], package['package_name'], version )
        else:
            url = 'https://pkgs.dev.azure.com/{}/_apis/packaging/feeds/{}/upack/packages/{}/versions/{}'.format(ORGANIZATION, feed['feed_id'], package['package_name'], version )
    else:
        console.print("[ERROR]: Unknown package_type -", package['package_type'], style="danger")
        raise typer.Abort()

    return url
