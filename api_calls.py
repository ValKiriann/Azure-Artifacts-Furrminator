import requests
from toolbox import generate_feed_list
import typer
from dotenv import load_dotenv
import os
from questions import *
import time
from PyInquirer import prompt
from rich.console import Console
from rich.theme import Theme
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red"
})
console = Console(theme=custom_theme)
load_dotenv()
PAT = os.getenv('PAT')
ORGANIZATION = os.getenv('ORGANIZATION')

def get_feeds(action_response, state):
    url = 'https://feeds.dev.azure.com/{}/_apis/Packaging/Feeds'.format(ORGANIZATION)
    headers = { 'Content-Type': 'application/json' }
    parameters = { 'api-version':'7.1-preview.1' }

    response = requests.get(url, params=parameters, headers=headers, auth=(PAT,''))
    status_code = response.status_code

    if state["verbose"]:
        console.print("[INFO]: Status Code of petition - Get Feeds", status_code, style="info")

    if status_code == 200:
        response_json = response.json()
        response_count = response_json['count']
        response_value = response_json['value']

        if state["verbose"]:
            console.print('[INFO]: I have found {0} results'.format(response_count), style="info")
            # time.sleep(1)

        return {'data': response_value, 'continue': True}
    else:
        console.print("[ERROR]: Get Feeds error -", response.content, style="danger")
        raise typer.Abort()
    
def get_packages(action_response, state):
    url = ''
    if 'feed' not in action_response:
        if not action_response['data']:
            action_response = get_feeds(action_response, state)
        feed_list = generate_feed_list(action_response, state)

        feed_list_question = questions = [
            {
                'type': 'list',
                'name': 'feed',
                'message': 'Select the feed to retrieve the package list: ',
                'choices': feed_list
            }
        ]
        selected_feed = prompt(feed_list_question)

        url = selected_feed['feed']
    else:
        url = action_response['feed']['value']

    headers = { 'Content-Type': 'application/json' }
    parameters = { 'api-version':'7.1-preview.1' }
    response = requests.get(url, params=parameters, headers=headers, auth=(PAT,''))
    status_code = response.status_code

    if state["verbose"]:
        console.print("[INFO]: Status Code of petition - get packages {}".format(status_code), style="info")

    if status_code == 200:
        response_json = response.json()
        response_count = response_json['count']
        response_value = response_json['value']
        if state["verbose"]:
            console.print('[INFO]: I have found {0} results'.format(response_count), style="info")
            # time.sleep(1)

        return {'data': response_value, 'continue': True}
    else:
        console.print("[ERROR]: Get Packages error -", response.content, style="danger")
        raise typer.Abort()

def get_versions(action_response, state):
    url = ''
    package_name = ''
    if len(action_response['data']) == 0:
        if state["verbose"]:
            console.print("[INFO]: Not enough information to get versions, asking user", style="info")
            # time.sleep(1)
        questions = [
            {
                'type': 'input',
                'name': 'input_feed',
                'message': "Enter Feed name of the package ('leave blank if you dont know')",
            },
            {
                'type': 'input',
                'name': 'input_package',
                'message': "Enter package ('leave blank if you prefer to select it from a list')",
            }
        ]

        answers = prompt(questions)
        if state["verbose"]:
            console.print("[INFO]: Answers: {}".format(answers), style="info")
            # time.sleep(1)
        input_feed = answers['input_feed']
        input_package = answers['input_package']

        if not input_feed and not input_package:
            console.print('[ERROR]: At least one of the parameters must be specified to start the search', style="danger")
            raise typer.Abort()
        if input_feed:
            get_feeds_response = get_feeds(action_response, state)
            if state["verbose"]:
                console.print("[INFO]: Received a feed in the input: {}. Proceeding to get feeds and look at the results to confirm a match".format(input_feed), style="info")
                # time.sleep(1)
            feed_list = generate_feed_list(get_feeds_response, state)
            selected_feed = {}
            for feed in feed_list:
                if feed['name'] == input_feed:
                    selected_feed = feed
                    break
            if len(selected_feed) == 0:
                console.print('[ERROR]: The feed {} was not found in Azure. Valid feeds are:'.format(input_feed), style="danger")
                for feed in feed_list:
                    console.print("  - {}".format(feed['name']), style="danger" )
                raise typer.Abort()

            if state["verbose"]:
                console.print("[INFO]: Proceeding to retrieve list of packages for feed provided: {}".format(input_feed), style="info")
                # time.sleep(1)
                
            action_response['feed'] = selected_feed
            if state["verbose"]:
                console.print("[INFO]: action_response: {}".format(action_response), style="info")
                # time.sleep(1)
            get_packages_response = get_packages(action_response, state)
            action_response['data'] = get_packages_response['data']

            if state["verbose"]:
                console.print("[INFO]: action response keys: {}".format(action_response.keys()), style="info")
                console.print("[INFO]: Number of packages found: {}".format(len(action_response['data'])), style="info")
                # time.sleep(1)

            package_list = list()
            for package in action_response['data']:
                package_list.append({ 'name':package['name'], 'value':package['_links']['versions']['href'] })

            if input_package:
                if state["verbose"]:
                    console.print("[INFO]: Received a package in the input: {}. Proceeding to look at the results to confirm a match".format(input_package), style="info")
                    # time.sleep(1)
                selected_package = {}
                for package in package_list:
                    if package['name'] == input_package:
                        selected_package = package
                        if state["verbose"]:
                            console.print("[INFO]: selected_package: {}".format(selected_package), style="info")
                            # time.sleep(1)
                        url = selected_package['value']
                        break
                if len(selected_package) == 0:
                    console.print('[ERROR]: The package {} was not found in Azure. Valid packages for the feed {} are:'.format(input_package, input_feed), style="danger")
                    for package in package_list:
                        console.print("  - {}".format(package['name']), style="danger" )
                    raise typer.Abort()
                else:
                    package_name = input_package
            else:
                if state["verbose"]:
                    console.print("[INFO]: No package name provided, generating list of packages for {} feed".format(input_feed), style="info")
                    # time.sleep(1)

                choose_package_question = choose_package_from_list_question(package_list)
                selected_package = prompt(choose_package_question)
                url = selected_package['package']

        else:
            # we dont have the feed but we got the package (or at least some kind of package)
            get_feeds_response = get_feeds(action_response)
            # TODO: for each feed retrieve list of package and look for it
            console.print("In progress", style="danger" )
            raise typer.Abort()
    else:
        if state["verbose"]:
            # console.print("[INFO]: action_response {}".format(action_response), style="info")
            console.print("[INFO]: Generating list of packages", style="info")
            # time.sleep(1)

        package_list = list()
        for package in action_response['data']:
            package_list.append({ 'name':package['name'], 'value':package['_links']['versions']['href'] })
                
        choose_package_question = choose_package_from_list_question(package_list)
        selected_package = prompt(choose_package_question)
        url = selected_package['package']

    
    if state["verbose"]:
        console.print("[INFO]: URL {}".format(url), style="info")
        # time.sleep(1)
                
    headers = { 'Content-Type': 'application/json' }
    parameters = { 'api-version':'7.1-preview.1' }

    for package in package_list:
        if package['value'] == url:
            package_name = package['name']
            break

    response = requests.get(url, params=parameters, headers=headers, auth=(PAT,''))
    status_code = response.status_code

    if state["verbose"]:
        console.print("[INFO]: Status Code of petition - get versions {}".format(status_code), style="info")

    if status_code == 200:
        response_json = response.json()
        response_count = response_json['count']
        response_value = response_json['value']

        if state["verbose"]:
            console.print('[INFO]: I have found {0} results'.format(response_count), style="info")
            # time.sleep(1)

        return {'data': response_value, 'package_name': package_name, 'continue': True}

    else:
        console.print("[ERROR]: Get Versions error -", response.content, style="danger")
        raise typer.Abort()