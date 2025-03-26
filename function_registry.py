"""
Function registry for the Software Engineering Bot.
This module defines the functions available to the OpenAI Assistant.
"""

def register_functions():
    """
    Register functions that can be called by the OpenAI assistant.
        
    Returns:
        list: The registered functions.
    """
    functions = [
        {
            "name": "fetch_project_issues",
            "description": "Fetch all issues for a specified project with optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "The name of the project. No capital letters."},
                    "status": {"type": "string", "description": "Filter issues by status, e.g., 'Open', 'In progress', 'Resolved', 'Blocked', 'Closed'. Always starting with capital letter."},
                    "priority": {"type": "string", "description": "Filter issues by priority, e.g., 'Critical', 'Major', 'Minor'."},
                    "issue_type": {"type": "string", "description": "Filter issues by type, e.g., 'Bug', 'Improvement', 'Task'."},
                    "assignee_id": {"type": "string", "description": "Filter issues by the ID of the assignee."},
                    "reporter_id": {"type": "string", "description": "Filter issues by the ID of the reporter."}
                },
                "required": ["project_name"]
            }
        },
        {
            "name": "get_issue_comments",
            "description": "Retrieve all comments for a specified issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_id": {"type": "string", "description": "The ID of the issue."}
                },
                "required": ["issue_id"]
            }
        },
        {
            "name": "count_issues",
            "description": "Count the number of issues in a project based on filters like developer ID, issue status, priority, or issue type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "The name of the project."},
                    "status": {"type": "string", "description": "Filter issues by status, e.g., 'Open', 'Closed', 'Resolved'."},
                    "priority": {"type": "string", "description": "Filter issues by priority, e.g., 'Critical', 'Major', 'Minor'."},
                    "issue_type": {"type": "string", "description": "Filter issues by type, e.g., 'Bug', 'Improvement', 'Task'."},
                    "assignee_id": {"type": "string", "description": "Filter issues by the ID of the assignee."},
                    "reporter_id": {"type": "string", "description": "Filter issues by the ID of the reporter."}
                },
                "required": ["project_name"]
            }
        },
        {
            "name": "get_project_assignees",
            "description": "Retrieve a list of assignees working on issues in a specific project and their total number, with optional filters such as issue priority or status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "The name of the project."
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter issues by status."
                    },
                    "priority": {
                        "type": "string",
                        "description": "Filter issues by priority."
                    },
                    "issue_type": {
                        "type": "string", 
                        "description": "Filter issues by type."
                    },
                    "reporter_id": {
                        "type": "string",
                        "description": "Filter issues by reporter ID."
                    }
                },
                "required": ["project_name"]
            }
        },
        {
            "name": "list_unique_values",
            "description": "List unique values of a specified attribute in the issue collection or other collections.",
            "parameters": {
                "type": "object",
                "properties": {
                    "collection_name": {"type": "string", "description": "The name of the MongoDB collection."},
                    "attribute_name": {"type": "string", "description": "The attribute for which to list unique values."},
                    "filters": {
                        "type": "object",
                        "description": "Filters to narrow down the unique values.",
                        "additionalProperties": True
                    }
                },
                "required": ["collection_name", "attribute_name", "filters"]
            }
        },
        {
            "name": "get_issue_details",
            "description": "Retrieve detailed information about a specific issue using approximate title matching, including comments, events, and related commits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_identifier": {"type": "string", "description": "The approximate title or ID of the issue to retrieve details for."}
                },
                "required": ["issue_identifier"]
            }
        },
        {
            "name": "analyze_developer_expertise",
            "description": "Analyze developer expertise to recommend the best assignee for an issue based on component and keyword experience.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "The name of the project."},
                    "component": {"type": "string", "description": "The component of the issue (e.g., 'security', 'authentication', 'ui')."},
                    "keywords": {"type": "string", "description": "Keywords related to the issue (e.g., 'authentication', 'bug', 'crash')."}
                },
                "required": ["project_name"]
            }
        }
    ]
    
    return functions