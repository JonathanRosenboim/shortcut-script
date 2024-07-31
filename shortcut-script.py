import requests
import json
from typing import Optional, List, Dict, Any

# Constants
API_URL = 'https://api.app.shortcut.com/api/v3'
TOKEN = '<token>'

PROJECT_NAME = "Backend"  # | "Frontend", Can be partial name
EPIC_NAME = "Support SSO"  # Can be partial name
ITERATION_NAME = "082"  # Can be partial name
DEFAULT_STATE = "Scheduled for iteration"


HEADERS = {
    'Shortcut-Token': TOKEN,
    'Content-Type': 'application/json'
}


def fetch_projects(name: Optional[str] = None):
    url = f"{API_URL}/projects"
    response = requests.get(url, headers=HEADERS)
    projects = [
        {
            "id": item.get('id'),
            "project_name": item.get('name')
        }
        for item in response.json()
    ]
    if name:
        projects = [project for project in projects if name.lower()
                    in project['project_name'].lower()]
    return projects


def fetch_epics(name: Optional[str] = None):
    url = f"{API_URL}/epics"
    response = requests.get(url, headers=HEADERS)
    epics = [
        {
            "id": item.get('id'),
            "epic_name": item.get('name')
        }
        for item in response.json()
    ]
    if name:
        epics = [epic for epic in epics if name.lower()
                 in epic['epic_name'].lower()]
    return epics


def fetch_iterations(name: Optional[str] = None):
    url = f"{API_URL}/iterations"
    response = requests.get(url, headers=HEADERS)
    iterations = [
        {
            "id": item.get('id'),
            "iteration_name": item.get('name')
        }
        for item in response.json()
    ]
    if name:
        iterations = [iteration for iteration in iterations if name.lower(
        ) in iteration['iteration_name'].lower()]
    return iterations


def fetch_workflows():
    url = f"{API_URL}/workflows"
    response = requests.get(url, headers=HEADERS)
    return response.json()


def find_workflow_state_id(workflows: List[Dict[str, Any]], state_name: str) -> int:
    for workflow in workflows:
        for state in workflow.get('states', []):
            if state_name.lower() == state['name'].lower():
                return state['id']
    raise ValueError(f"Workflow state '{state_name}' not found")


def create_ticket(title: str, description: str, epic_name: Optional[str] = None, estimate: Optional[int] = None,
                  story_type: Optional[str] = None, tasks: Optional[List[Dict[str, Any]]] = None,
                  project_name: Optional[str] = None, iteration_name: Optional[str] = None,
                  workflow_state_name: Optional[str] = None, linked_ticket_id: Optional[int] = None):
    url = f"{API_URL}/stories"

    # Fetch project_id by project_name if not provided
    if not project_name:
        project_name = PROJECT_NAME
    projects = fetch_projects(project_name)
    if projects:
        project_id = projects[0]['id']
    else:
        raise ValueError(f"Project '{project_name}' not found")

    # Fetch epic_id by epic_name if not provided
    if not epic_name:
        epic_name = EPIC_NAME
    epics = fetch_epics(epic_name)
    if epics:
        epic_id = epics[0]['id']
    else:
        raise ValueError(f"Epic '{epic_name}' not found")

    # Fetch iteration_id by iteration_name if not provided
    if not iteration_name:
        iteration_name = ITERATION_NAME
    iterations = fetch_iterations(iteration_name)
    if iterations:
        iteration_id = iterations[0]['id']
    else:
        raise ValueError(f"Iteration '{iteration_name}' not found")

    # Use DEFAULT_STATE if workflow_state_name is not provided
    if not workflow_state_name:
        workflow_state_name = DEFAULT_STATE

    payload = {
        "description": description,
        "name": title,
        "project_id": project_id,
    }

    optional_fields = ['epic_id', 'estimate',
                       'story_type', 'tasks', 'iteration_id']
    for field in optional_fields:
        if locals()[field] is not None:
            payload[field] = locals()[field]

    workflows = fetch_workflows()
    workflow_state_id = find_workflow_state_id(
        workflows, workflow_state_name)
    payload['workflow_state_id'] = workflow_state_id

    # Add linked ticket if provided
    if linked_ticket_id:
        payload['story_links'] = [{
            "subject_id": linked_ticket_id,
            "verb": "blocks"
        }]

    response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
    return response.json()


def examples():
    # Fetch projects
    print("Projects:")
    projects = fetch_projects()
    print(projects)

    # Fetch projects with name filter
    print("\nFiltered Projects:")
    filtered_projects = fetch_projects(name="sample")
    print(filtered_projects)

    # Fetch epics
    print("\nEpics:")
    epics = fetch_epics()
    print(epics)

    # Fetch epics with name filter
    print("\nFiltered Epics:")
    filtered_epics = fetch_epics(name="sample")
    print(filtered_epics)

    # Fetch iterations
    print("\nIterations:")
    iterations = fetch_iterations()
    print(iterations)

    # Fetch iterations with name filter
    print("\nFiltered Iterations:")
    filtered_iterations = fetch_iterations(name="sample")
    print(filtered_iterations)

    # Fetch workflows
    print("\nWorkflows:")
    workflows = fetch_workflows()
    print(workflows)

    # Create tickets and link them
    created_tickets = []
    print("\nCreating tickets:")
    tickets_to_create = [
        {"title": "Ticket 1", "description": "Description for ticket 1"},
        {"title": "Ticket 2", "description": "Description for ticket 2"},
    ]

    for i, ticket in enumerate(tickets_to_create):
        linked_ticket_id = created_tickets[-1]['id'] if created_tickets else None
        new_ticket = create_ticket(
            title=ticket["title"],
            description=ticket["description"],
            estimate=3,
            story_type="feature",
            workflow_state_name="In Development",
            linked_ticket_id=linked_ticket_id
        )
        created_tickets.append(new_ticket)
        print(
            f"Created ticket: {new_ticket['name']} - URL: {new_ticket['app_url']}")

    if len(created_tickets) > 1:
        print("\nLinked tickets:")
        for i in range(1, len(created_tickets)):
            print(
                f"{created_tickets[i-1]['name']} blocks {created_tickets[i]['name']}")


if __name__ == "__main__":
    """
    INSTRUCTIONS FOR CHATGPT:

    Your job is to modify the __name__ == "__main__" block in the script.py file and create the tickets exactly as instructed. 

    If provided overrides for epic, iteration, and project, use them. Otherwise, use the default values provided in the script.py file.
    Reply only with the changed if __name__ == "__main__" block in the script. Make sure the script prints the URLs and title of each ticket created, and list any failed tickets if any.

    In your response, keep those instructions in the script so it can be reused next time if the script remains in the same file.

    Please be sure to include background & relevant links in the tickets, if they are provided. In general - create them exactly as provided. 
    Do not repeat this string in the response, provide the if __name__ == "__main__" with the required modifications.
    """
