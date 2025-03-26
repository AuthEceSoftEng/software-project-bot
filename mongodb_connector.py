"""
MongoDB connector for the Software Engineering Bot.
This module handles all interactions with the MongoDB database.
"""

import pymongo
from bson import ObjectId
import datetime
import json

class MongoDBConnector:
    """
    MongoDB connector for the Software Engineering Bot.
    This class handles all interactions with the MongoDB database.
    """
    
    def __init__(self, db):
        """
        Initialize the MongoDB connector.
        
        Args:
            db: The MongoDB database object.
        """
        self.db = db

    def get_collection_schemas(self):
        """
        Get the schema of each collection in the database.
        
        Returns:
            dict: A dictionary mapping collection names to their schemas.
        """
        schemas = {}
        collections = self.db.list_collection_names()
        for collection in collections:
            sample_doc = self.db[collection].find_one()
            if sample_doc:
                schemas[collection] = {key: type(value).__name__ for key, value in sample_doc.items()}
            else:
                schemas[collection] = {}
        return schemas

    def serialize_mongo_doc(self, doc):
        """
        Serialize a MongoDB document to a JSON-serializable format.
        
        Args:
            doc: The document to serialize.
            
        Returns:
            The serialized document.
        """
        if isinstance(doc, list):
            return [self.serialize_mongo_doc(d) for d in doc]
        elif isinstance(doc, dict):
            return {key: self.serialize_mongo_doc(value) for key, value in doc.items()}
        elif isinstance(doc, ObjectId):
            return str(doc)
        elif isinstance(doc, datetime.datetime):
            return doc.isoformat()
        else:
            return doc

    def fetch_project_issues(self, project_name, status=None, priority=None, issue_type=None, 
                           assignee_id=None, reporter_id=None, page=1, page_size=50):
        """
        Fetch all issues for a specified project with optional filters.
        
        Args:
            project_name (str): The name of the project.
            status (str, optional): Filter issues by status.
            priority (str, optional): Filter issues by priority.
            issue_type (str, optional): Filter issues by type.
            assignee_id (str, optional): Filter issues by assignee ID.
            reporter_id (str, optional): Filter issues by reporter ID.
            page (int, optional): The page number for pagination.
            page_size (int, optional): The number of issues per page.
            
        Returns:
            dict: The issues matching the filters.
        """
        try:
            # Fetch the project by name
            project = self.db["project"].find_one({"name": project_name})
            if not project:
                return {"error": f"Project '{project_name}' not found."}

            # Get all issue systems for the project
            issue_systems = self.db["issue_system"].find({"project_id": project["_id"]})
            issue_systems_list = list(issue_systems)
            issue_system_ids = [system["_id"] for system in issue_systems_list]
            
            # Build the query dynamically
            query = {"issue_system_id": {"$in": issue_system_ids}}
            
            if status:
                query["status"] = status
            if priority:
                query["priority"] = priority
            if issue_type:
                query["issue_type"] = issue_type
            if assignee_id:
                query["assignee_id"] = ObjectId(assignee_id) if ObjectId.is_valid(assignee_id) else assignee_id
            if reporter_id:
                query["reporter_id"] = ObjectId(reporter_id) if ObjectId.is_valid(reporter_id) else reporter_id

            # Skip and limit for pagination
            skip = (page - 1) * page_size
            issues = list(self.db["issue"].find(query).skip(skip).limit(page_size))
            
            return {
                "issues": self.serialize_mongo_doc(issues), 
                "page": page, 
                "page_size": page_size,
                "total_count": self.db["issue"].count_documents(query)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def count_issues(self, project_name, status=None, priority=None, issue_type=None, 
                   assignee_id=None, reporter_id=None):
        """
        Count the number of issues in a project based on filters.
        
        Args:
            project_name (str): The name of the project.
            status (str, optional): Filter issues by status.
            priority (str, optional): Filter issues by priority.
            issue_type (str, optional): Filter issues by type.
            assignee_id (str, optional): Filter issues by assignee ID.
            reporter_id (str, optional): Filter issues by reporter ID.
            
        Returns:
            dict: The count of issues matching the filters.
        """
        try:
            # Fetch the project by name
            project = self.db["project"].find_one({"name": project_name})
            if not project:
                return {"error": f"Project '{project_name}' not found."}

            # Get all issue systems for the project
            issue_systems = self.db["issue_system"].find({"project_id": project["_id"]})
            issue_system_ids = [system["_id"] for system in issue_systems]

            # Build the query dynamically
            query = {"issue_system_id": {"$in": issue_system_ids}}

            if status:
                query["status"] = status
            if priority:
                query["priority"] = priority
            if issue_type:
                query["issue_type"] = issue_type
            if assignee_id:
                query["assignee_id"] = ObjectId(assignee_id) if ObjectId.is_valid(assignee_id) else assignee_id
            if reporter_id:
                query["reporter_id"] = ObjectId(reporter_id) if ObjectId.is_valid(reporter_id) else reporter_id

            # Count documents matching the query
            count = self.db["issue"].count_documents(query)

            return {"count": count}
        except Exception as e:
            return {"error": str(e)}
    
    def list_unique_values(self, collection_name, attribute_name, filters=None):
        """
        List unique values of a specified attribute in a MongoDB collection.
        
        Args:
            collection_name (str): The name of the collection.
            attribute_name (str): The attribute to get unique values for.
            filters (dict, optional): Filters to apply to the query.
            
        Returns:
            dict: The unique values.
        """
        try:
            # Validate collection name
            if collection_name not in self.db.list_collection_names():
                return {"error": f"Collection '{collection_name}' does not exist."}

            # Build the query with optional filters
            query = filters if filters else {}

            # Get unique values
            unique_values = self.db[collection_name].distinct(attribute_name, query)

            return {"unique_values": self.serialize_mongo_doc(unique_values)}
        except Exception as e:
            return {"error": str(e)}

    def get_project_assignees(self, project_name, status=None, priority=None, issue_type=None, reporter_id=None):
        """
        Retrieve a list of assignees working on issues in a specific project, with optional filters.
        
        Args:
            project_name (str): The name of the project.
            status (str, optional): Filter by issue status.
            priority (str, optional): Filter by issue priority.
            issue_type (str, optional): Filter by issue type.
            reporter_id (str, optional): Filter by reporter ID.
            
        Returns:
            dict: The assignees matching the filters.
        """
        try:
            # Fetch the project by name
            project = self.db["project"].find_one({"name": project_name})
            if not project:
                return {"error": f"Project '{project_name}' not found."}

            # Get all issue systems for the project
            issue_systems = self.db["issue_system"].find({"project_id": project["_id"]})
            issue_systems_list = list(issue_systems)
            issue_system_ids = [system["_id"] for system in issue_systems_list]
            
            # Build the query
            query = {"issue_system_id": {"$in": issue_system_ids}}
            
            if status:
                query["status"] = status
            if priority:
                query["priority"] = priority
            if issue_type:
                query["issue_type"] = issue_type
            if reporter_id:
                query["reporter_id"] = ObjectId(reporter_id) if ObjectId.is_valid(reporter_id) else reporter_id
                
            # Fetch issues matching the query
            issues = list(self.db["issue"].find(query, {"assignee_id": 1}))
            
            # Extract unique assignee IDs from the issues
            assignee_ids = list({issue["assignee_id"] for issue in issues if "assignee_id" in issue})
            
            return {"assignees": self.serialize_mongo_doc(assignee_ids), "count": len(assignee_ids)}
        except Exception as e:
            return {"error": str(e)}
            
    def get_issue_details(self, issue_identifier):
        """
        Retrieve detailed information about a specific issue.
        
        Args:
            issue_identifier (str): The identifier of the issue.
            
        Returns:
            dict: The issue details.
        """
        try:
            # Determine the query based on user input
            query = {}
            query["external_id"] = issue_identifier
            
            # Retrieve the issue
            issue = self.db["issue"].find_one(query)
            if not issue:
                return {"error": f"Issue matching '{issue_identifier}' not found."}

            # Retrieve related comments
            comments = list(self.db["issue_comment"].find({"issue_id": issue["_id"]}))

            # Retrieve related events
            events = list(self.db["event"].find({"issue_id": issue["_id"]}))

            # Retrieve related commits
            linked_commits = list(self.db["commit"].find({"linked_issue_ids": issue["_id"]}))

            # Serialize data
            return {
                "issue": self.serialize_mongo_doc(issue),
                "comments": self.serialize_mongo_doc(comments),
                "events": self.serialize_mongo_doc(events),
                "linked_commits": self.serialize_mongo_doc(linked_commits),
            }
        except Exception as e:
            return {"error": str(e)}
            
    def get_issue_comments(self, issue_id):
        """
        Retrieve all comments for a specified issue.
        
        Args:
            issue_id (str): The ID of the issue.
            
        Returns:
            dict: The comments for the issue.
        """
        try:
            comments = list(self.db["issue_comment"].find({"issue_id": issue_id}))
            return {"comments": self.serialize_mongo_doc(comments)}
        except Exception as e:
            return {"error": str(e)}
            
    def analyze_developer_expertise(self, project_name, component=None, keywords=None):
        """
        Analyze developer expertise to recommend the best assignee for an issue.
        Implementation of Use Case 2 from the paper.
        
        Args:
            project_name (str): The name of the project.
            component (str, optional): The component of the issue.
            keywords (str, optional): Keywords related to the issue.
            
        Returns:
            dict: Developer recommendations with expertise scores.
        """
        try:
            # Get all assignees in the project
            assignees_result = self.get_project_assignees(project_name=project_name)
            
            if "error" in assignees_result:
                return assignees_result
                
            assignees = assignees_result.get("assignees", [])
            
            # List to store recommendations
            recommendations = []
            
            for assignee_id in assignees:
                # Skip if assignee_id is None
                if not assignee_id:
                    continue
                    
                # Calculate expertise score based on component and keywords
                expertise_score = 0
                component_experience = 0
                keyword_experience = 0
                resolved_count = 0
                
                # Check component experience if specified
                if component:
                    # Query issues by assignee and component
                    # In this simplified version, we use the component as a term to search in issue titles
                    component_query = {"$and": [
                        {"issue_system_id": {"$in": self._get_issue_system_ids(project_name)}},
                        {"assignee_id": assignee_id},
                        {"$or": [
                            {"component": {"$regex": component, "$options": "i"}},
                            {"title": {"$regex": component, "$options": "i"}}
                        ]}
                    ]}
                    
                    component_experience = self.db["issue"].count_documents(component_query)
                
                # Check keyword experience if specified
                if keywords:
                    # Query issues by assignee and keywords in title or description
                    keyword_query = {"$and": [
                        {"issue_system_id": {"$in": self._get_issue_system_ids(project_name)}},
                        {"assignee_id": assignee_id},
                        {"$or": [
                            {"title": {"$regex": keywords, "$options": "i"}},
                            {"desc": {"$regex": keywords, "$options": "i"}}
                        ]}
                    ]}
                    
                    keyword_experience = self.db["issue"].count_documents(keyword_query)
                
                # Get total resolved issues for this assignee
                resolved_query = {"$and": [
                    {"issue_system_id": {"$in": self._get_issue_system_ids(project_name)}},
                    {"assignee_id": assignee_id},
                    {"status": "Resolved"}
                ]}
                
                resolved_count = self.db["issue"].count_documents(resolved_query)
                
                # Calculate overall expertise score
                # Weight component experience more heavily
                expertise_score = component_experience * 2 + keyword_experience + resolved_count
                
                # Only include developers with some expertise
                if expertise_score > 0:
                    # Get developer name or use ID if name not available
                    developer_name = f"Dev-{assignee_id[-4:]}" if isinstance(assignee_id, str) else f"Dev-{str(assignee_id)}"
                    
                    recommendations.append({
                        "developer_id": str(assignee_id),
                        "developer_name": developer_name,
                        "expertise_score": expertise_score,
                        "component_experience": component_experience,
                        "keyword_experience": keyword_experience,
                        "resolved_issues": resolved_count
                    })
            
            # Sort recommendations by expertise score (highest first)
            recommendations.sort(key=lambda x: x["expertise_score"], reverse=True)
            
            # Return top 3 recommendations or all if fewer than 3
            top_recommendations = recommendations[:3] if len(recommendations) >= 3 else recommendations
            
            return {
                "recommendations": top_recommendations,
                "total_candidates": len(recommendations)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_issue_system_ids(self, project_name):
        """
        Helper method to get issue system IDs for a project.
        
        Args:
            project_name (str): The name of the project.
            
        Returns:
            list: A list of issue system IDs.
        """
        # Fetch the project by name
        project = self.db["project"].find_one({"name": project_name})
        if not project:
            return []
            
        # Get all issue systems for the project
        issue_systems = self.db["issue_system"].find({"project_id": project["_id"]})
        return [system["_id"] for system in issue_systems]