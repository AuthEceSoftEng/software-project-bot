# Software Engineering Bot

A conversational bot for querying software repository data through natural language, as described in the paper "Software Engineering Bot: A Modular Pipeline for Natural Language Repository Mining".

## Overview

This bot allows users to interact with software repository data through natural language queries. It leverages OpenAI's API and a MongoDB database to answer questions about software projects, issues, developers, and more.

## Features

- Query software repositories using natural language
- Get issue statistics with filtering by status, priority, and more
- Receive developer recommendations for issue assignments based on expertise
- Analyze issue details including comments, events, and linked commits
- Multi-turn conversations with context maintenance


## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your MongoDB connection string and OpenAI API key (see `.env.example`)
4. Run the bot: `python main.py`

## Requirements

- Python 3.8+
- MongoDB database with software repository data
- OpenAI API key with access to GPT-4o

## Project Structure

- `main.py`: Main application with conversation loop
- `mongodb_connector.py`: MongoDB connection and data access functions
- `function_registry.py`: Function definitions for the bot
- `event_handler.py`: Event handler for OpenAI Assistant API

## How It Works

1. User enters a natural language query
2. LLM processes the query to determine intent and extract entities
3. The appropriate functions are called to retrieve data from MongoDB
4. Results are processed and returned to the user in natural language
