"""
Event handler for the Software Engineering Bot.
This module handles events from the OpenAI Assistant API.
"""

import json
import time
from typing_extensions import override
from openai import AssistantEventHandler

class EventHandler(AssistantEventHandler):
    """
    Event handler for the OpenAI Assistant API.
    Handles stream events and tool calls.
    """
    
    def __init__(self, mongodb_connector):
        """
        Initialize the event handler.
        
        Args:
            mongodb_connector: The MongoDB connector.
        """
        super().__init__()
        self.response_text = ""
        self.tool_outputs = []
        self.run_id = None
        self.all_tools_done = False  # Track whether all tools are finished
        self.tools_called = False    # Track if any tools are called
        self.connector = mongodb_connector
        
    @override
    def on_event(self, event):
        """
        Handle OpenAI Assistant events.
        
        Args:
            event: The event to handle.
        """
        # Handle events that require action
        if event.event == "thread.run.requires_action":
            self.run_id = event.data.id  # Store the run ID
            self.tools_called = True  # Tools are being called
            self.handle_requires_action(event.data)
            
    def handle_requires_action(self, data):
        """
        Handle events that require action.
        
        Args:
            data: The data from the event.
        """
        tool_outputs = []
        
        for tool_call in data.required_action.submit_tool_outputs.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Log the tool call
            print(f"\n[Tool called: {func_name} with arguments: {args}]", end="")
            
            # Route to the correct function
            if func_name == "fetch_project_issues":
                result = self.connector.fetch_project_issues(
                    project_name=args["project_name"],
                    status=args.get("status"),
                    priority=args.get("priority"),
                    issue_type=args.get("issue_type"),
                    assignee_id=args.get("assignee_id"),
                    reporter_id=args.get("reporter_id"),
                    page=args.get("page", 1),
                    page_size=args.get("page_size", 50)
                )
            elif func_name == "count_issues":
                result = self.connector.count_issues(
                    project_name=args["project_name"],
                    status=args.get("status"),
                    priority=args.get("priority"),
                    issue_type=args.get("issue_type"),
                    assignee_id=args.get("assignee_id"),
                    reporter_id=args.get("reporter_id")
                )
            elif func_name == "list_unique_values":
                result = self.connector.list_unique_values(
                    collection_name=args["collection_name"],
                    attribute_name=args["attribute_name"],
                    filters=args.get("filters")
                )
            elif func_name == "get_project_assignees":
                result = self.connector.get_project_assignees(
                    project_name=args["project_name"],
                    status=args.get("status"),
                    priority=args.get("priority"),
                    issue_type=args.get("issue_type"),
                    reporter_id=args.get("reporter_id")
                )
            elif func_name == "get_issue_details":
                result = self.connector.get_issue_details(args["issue_identifier"])
            elif func_name == "get_issue_comments":
                result = self.connector.get_issue_comments(args["issue_id"])
            elif func_name == "analyze_developer_expertise":
                result = self.connector.analyze_developer_expertise(
                    project_name=args["project_name"],
                    component=args.get("component"),
                    keywords=args.get("keywords")
                )
            else:
                result = {"error": "Unsupported function call."}
                
            # Append the result to tool outputs
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })
            
        self.tool_outputs = tool_outputs
        self.all_tools_done = True
        
    def wait_for_tools(self, timeout=5):
        """
        Wait until all tool outputs are handled or timeout.
        
        Args:
            timeout: The timeout in seconds.
        """
        start_time = time.time()
        
        while not self.all_tools_done:
            if not self.tools_called or (time.time() - start_time > timeout):
                break
            time.sleep(0.1)
            
    def on_text_delta(self, delta, snapshot):
        """
        Handle text deltas from the Assistant.
        
        Args:
            delta: The text delta.
            snapshot: The current text snapshot.
        """
        if delta.value:
            print(delta.value, end="", flush=True)
            self.response_text += delta.value
            
    def on_text_done(self, text):
        """
        Handle text completion.
        
        Args:
            text: The completed text.
        """
        print("\n")  # Ensure a blank line between assistant responses
        
    def on_exception(self, exception):
        """
        Handle exceptions during streaming.
        
        Args:
            exception: The exception that occurred.
        """
        print(f"\nException during streaming: {exception}")