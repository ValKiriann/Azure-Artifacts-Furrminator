from api_calls import delete_version
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

'''
@function delete
@param {dictionary} response_data - The last raw response from an api call
    response_data {
        data: {... last raw api response ...},
        continue: Bool, to control wheter to continue the flow or exit,
        feed: {... details of the selected feed...} see sanitize_feed_info,
        package: {... details of the selected package...} see sanitize_package_info,
        versions: {... dictionary that contains versions related to the package ...} see obtain_versions_from_package for structure
    }
@param {dictionary} state - Object that contains the state of the tool
@description    This function prepares deletion bulk of a package
'''
def delete(response_data, state):
    versions = response_data['versions']
    version = typer.prompt("Enter the version to delete")
    print(version)
    print(response_data.keys())
    if version in versions['versions_array']:
        # print('Version {} found'.format(version))

        if version in versions['prediction']['versions_array_delete']:
            console.print('Version {} was found in the prediction policy to delete'.format(version))
        else:
            console.print('[warning]: Version {} was not found in the prediction policy to delete'.format(version), style="warning")

        delete = typer.confirm("Are you sure you want to delete it?", abort=True)
        print('Version {} was deleted successfully'.format(version))
        raise typer.Exit()
    else:
        print('version {} not found'.format(version))
        console.print('[ERROR]: version {} not found'.format(version), style="danger")
        console.print('[ERROR]: Current listed versions for {}: {}'.format(response_data['package_name'], versions['versions_array']), style="danger")
        raise typer.Exit()

'''
@function delete_in_bulk
@param {dictionary} response_data - The last raw response from an api call
    response_data {
        data: {... last raw api response ...},
        continue: Bool, to control wheter to continue the flow or exit,
        feed: {... details of the selected feed...} see sanitize_feed_info,
        package: {... details of the selected package...} see sanitize_package_info,
        versions: {... dictionary that contains versions related to the package ...} see obtain_versions_from_package for structure
    }
@param {dictionary} state - Object that contains the state of the tool
@description    This function prepares deletion bulk of a package
'''
def bulk_delete(response_data, state):
    package = response_data['package']
    feed = response_data['feed']
    errors = []
    for version in package['versions_array_delete']:
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

        delete_result = delete_version(url, state)
        if type(delete_result) != bool:
            errors.append({version: delete_result})

    response_data['delete_errors'] = errors

    return response_data