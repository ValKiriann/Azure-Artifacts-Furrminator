#!/usr/bin/python3
from questions import *
import versions_controller
from toolbox import asciiLogo, createTableInfo, create_versions_table_info, predict_versions_to_clean, exit
from api_calls import get_feeds, get_packages, get_versions
import typer
from PyInquirer import prompt
from rich import print as rprint
from rich.console import Console
from rich.theme import Theme
import json
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red"
})
console = Console(theme=custom_theme)

methods = { 
    'get_feeds': {
        'call': get_feeds,
    },
    'start': {
        'call': 'start',
    },
    'get_packages': {
        'call': get_packages,
    },
    'exit': {
        'call': exit,
    },
    'get_versions': {
        'call': get_versions,
    },
    'select_bulk_deletion': {
        'call': predict_versions_to_clean
    },
    'delete_version': {
        'call': versions_controller.delete
    }
}

sub_methods = {
    'view_table': {
        'call': createTableInfo,
    },
    'view_versions_table': {
        'call': create_versions_table_info
    },
}

app = typer.Typer()
state = {"verbose": False}

@app.command("init")
def init():

    rprint(asciiLogo())
    rprint("[orchid1 bold]Welcome to Furrminator[/orchid1 bold] the Azure Artifacts removal tool")

    actual_action = 'start'
    action_response = {'data': [], 'continue': True}

    while actual_action != 'exit':
        if actual_action == 'start':
            method_list_question = start_questions_list
        elif actual_action == 'get_feeds':
            method_list_question = get_feeds_questions_list
        elif actual_action == 'get_packages':
            method_list_question = get_packages_questions_list
        elif actual_action == 'get_versions':
            method_list_question = get_versions_questions_list
        # elif actual_action == 'delete_version':
        #     delete_controller.delete_version(action_response, state)

        #     raise typer.Exit()
        elif actual_action == 'select_bulk_deletion':
            delete = typer.confirm("Are you sure you want to delete it?", abort=True)
            print("Proceeding to delete")
            delete_response = versions_controller.bulk_delete(action_response, state)
            if len(delete_response['delete_errors']) > 0:
                console.print('[ERROR]: Errors where found while deleting', style="danger")
                console.print(json.dumps(delete_response['delete_errors'], indent=2), style="danger")
            else:
                print('Versions were deleted successfully')
                exit(action_response, state)

            raise typer.Exit()
        else:
            console.print("[ERROR]: Unknown action -", actual_action, style="danger")
            raise typer.Abort()

        selected_action = prompt(method_list_question)
        rprint("[yellow]=============================================[yello]")

        if selected_action['action'] in methods.keys():
            selected_action = selected_action['action']
            action_response = methods[selected_action]['call'](action_response, state)
            actual_action = selected_action
            # if action_response['continue']:
            #     actual_action = selected_action
            # else:
            #     actual_action = exit
        else:
            sub_methods[selected_action['action']]['call'](action_response, state)

@app.command("hello")
def hello():
    rprint(asciiLogo())
    rprint("Welcome to [orchid1 bold]Furrminator[/orchid1 bold], the Azure Artifacts removal tool") 
    rprint("Furrminator is your personalized Azure Artifacts removal tool")
    print()
    rprint("Gifted to you by [orchid1 bold]ana.enriqueza[/orchid1 bold] @Softtek2023 💖") 

@app.callback()
def main(verbose: bool = False):
    """
    Manage artifact deletion in the Furrminator CLI app.
    """
    if verbose:
        console.print("[INFO]: Will write verbose output", style="info")
        state["verbose"] = True

if __name__ == "__main__":
    app()