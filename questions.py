start_questions_list = questions = [
    {
        'type': 'list',
        'name': 'action',
        'message': 'Select what do you want to do: ',
        'choices': [
            {
                'name': 'Get Feeds',
                'value': 'get_feeds'
            },
            {
                'name': 'Get Packages',
                'value': 'get_packages'
            },
            {
                'name': 'Get Versions of a Package',
                'value': 'get_versions'
            },
            {
                'name': 'Exit',
                'value': 'exit'
            },
        ],
    }
]
get_feeds_questions_list = questions = [
    {
        'type': 'list',
        'name': 'action',
        'message': 'Select what do you want to do: ',
        'choices': [
            {
                'name': 'List information of the feeds',
                'value': 'view_table'
            },
            {
                'name': 'Select a feed to list all packages',
                'value': 'get_packages'
            },
            {
                'name': 'Exit',
                'value': 'exit'
            },
        ],
    }
]
get_packages_questions_list = questions = [
    {
        'type': 'list',
        'name': 'action',
        'message': 'Select what do you want to do: ',
        'choices': [
            {
                'name': 'List information of the packages',
                'value': 'view_table'
            },
            {
                'name': 'Select a package to list all versions',
                'value': 'get_versions'
            },
            {
                'name': 'Exit',
                'value': 'exit'
            },
        ],
    }
]

def choose_package_from_list_question(package_list):
    choose_package_from_list_question = questions = [
        {
            'type': 'list',
            'name': 'package',
            'message': 'Select the package to retrieve the package list:',
            'choices': package_list
        }
    ]
    return choose_package_from_list_question

get_versions_questions_list = questions = [
    {
        'type': 'list',
        'name': 'action',
        'message': 'Select what do you want to do: ',
        'choices': [
            {
                'name': 'Describe versions',
                'value': 'view_versions_table'
            },
            {
                'name': 'Show all versions to delete',
                'value': 'select_bulk_deletion'
            },
            {
                'name': 'Delete Specific version',
                'value': 'delete_version'
            },
            {
                'name': 'Exit',
                'value': 'exit'
            },
        ],
    }
]