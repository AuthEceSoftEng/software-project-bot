"""
Main application file for the Software Engineering Bot.
This module initializes the bot and starts the conversation loop.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import pymongo
from mongodb_connector import MongoDBConnector
from function_registry import register_functions
from event_handler import EventHandler

def main():
    """
    Main entry point for the Software Engineering Bot.
    Initializes connections and starts the conversation loop.
    """
    # Load environment variables
    load_dotenv()
    
    # MongoDB Connection
    mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
    mongo_database_name = os.getenv("MONGO_DATABASE_NAME")
    
    # Connect to MongoDB
    print(f"Connecting to MongoDB database: {mongo_database_name}...")
    mongo_client = pymongo.MongoClient(mongo_connection_string)
    db = mongo_client[mongo_database_name]
    
    # Initialize MongoDB connector
    connector = MongoDBConnector(db)
    
    # Get database schema
    schema = connector.get_collection_schemas()
    
    # OpenAI Client
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_api_key)
    
    # Register functions
    functions = register_functions()
    
    # Create assistant with instructions and functions
    instructions = f"""
    You are a chatbot for querying a software project's MongoDB database. Use the provided functions to fetch relevant data based on user input.
    
    The identifier id of issues is in the format of 'ZOOKEEPER-1939' if given without all capitals, capitalize. 
    The status of issues can be 'Open', 'In Progress' or 'Closed'.
    
    You can handle two primary use cases as described in the "Software Engineering Bot" research paper:
    
    1. Issue Statistics Query: Providing statistics about issues in a project, including filtering by status, priority, etc.
       Example: "How many open issues are there in the Zookeeper project, and what percentage of them are critical?"
    
    2. Developer Assignment Recommendation: Recommending developers for issue assignment based on their expertise and experience.
       Example: "Who would be the best developer to assign this authentication bug in the security component of the Hadoop project?"
    
    Here is the structure of the database to assist you in crafting accurate responses:
    
    **Collections and Descriptions:**
    - `pull_request_comment`: Comments associated with pull requests, including author and creation details.
    - `mailing_list`: Metadata about mailing lists for projects, such as project ID and name.
    - `travis_build`: Information about Travis CI builds, including build state and duration.
    - `vcs_system`: Version control system details, such as repository type and URL.
    - `pull_request_system`: Details about pull request systems, like the associated project ID and URL.
    - `pull_request_file`: Information about files involved in pull requests, including changes and additions.
    - `issue`: Details about issues, including title, description, priority, and status.
    - `file`: Metadata about files in the version control system.
    - `pull_request_review_comment`: Comments on pull request reviews, including paths and diffs.
    - `project`: Contains project names and IDs.
    - `event`: Events related to issues, including status changes and authors.
    - `refactoring`: Refactoring information, including detection tools and commit details.
    - `commit`: Details about commits, including authors, linked issues, and labels.
    - `tag`: Tags associated with commits in the version control system.
    - `file_action`: Actions performed on files during commits, such as additions and deletions.
    - `issue_system`: Metadata about issue tracking systems, like URLs and project IDs.
    - `commit_changes`: Details about changes between commits, including classifications.
    - `message`: Mailing list messages, including authors, subjects, and bodies.
    - `pull_request_commit`: Commit information related to pull requests.
    - `pull_request_review`: Metadata about pull request reviews, including states and descriptions.
    - `issue_comment`: Comments on issues, including author and creation details.
    - `pull_request`: Metadata about pull requests, such as titles, states, and associated repositories.
    - `pull_request_event`: Events related to pull requests, like commits and changes.
    - `branch`: Metadata about branches in the version control system.
    - `hunk`: Detailed code changes in commits, including line additions and deletions.
    
    Use the above information to guide users in querying the database effectively. Always aim to provide clear and concise answers, and if a query is ambiguous, ask for clarification.
    
    When recommending developers for issue assignment, explain your reasoning based on their experience with similar components, keywords, and past issue resolution.
    
    {json.dumps(schema, indent=4)}
    """
    
    print("Creating OpenAI Assistant...")
    assistant = client.beta.assistants.create(
        name="Software Engineering Bot",
        instructions=instructions,
        model=os.getenv("OPENAI_MODEL"),
        tools=[{"type": "function", "function": func} for func in functions]
    )
    
    # Create a thread for the conversation
    thread = client.beta.threads.create()
    
    print("\nSoftware Engineering Bot initialized. Type 'exit' to quit.")
    print("=====================================")
    
    # Conversation loop
    while True:
        user_input = input("\nYou > ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("\nExiting the conversation.")
            break
        
        # Add user message to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        
        # Create a new EventHandler instance for each stream
        handler = EventHandler(connector)
        
        try:
            print("\nAssistant > ", end="")  # Print Assistant prefix before starting
            
            # Start the assistant response stream
            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                event_handler=handler,
                max_prompt_tokens=10000
            ) as stream:
                stream.until_done()
                
            handler.wait_for_tools()
            
            # If there are tool outputs to submit, submit them
            if handler.tool_outputs:
                # Create a new EventHandler instance for tool outputs stream
                tool_handler = EventHandler(connector)
                
                with client.beta.threads.runs.submit_tool_outputs_stream(
                    thread_id=thread.id,
                    run_id=handler.run_id,  # Use the stored run ID
                    tool_outputs=handler.tool_outputs,
                    event_handler=tool_handler
                ) as tool_stream:
                    tool_stream.until_done()
        
        except Exception as e:
            print(f"Error during processing: {e}")
        
        print("\n")  # Blank line for readability

if __name__ == "__main__":
    main()