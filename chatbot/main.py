from google.adk.tools import FunctionTool, ToolContext
from google.adk.agents import LlmAgent, Agent, SequentialAgent, ParallelAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import UnsafeLocalCodeExecutor
from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
import google.generativeai as genai
import asyncio
import uuid
import os
import psycopg2
import mysql.connector
from dotenv import load_dotenv
import duckdb
import pprint
import pandas as pd
import re
from google.adk.agents import LiveRequestQueue
from google.genai import types
import google.generativeai as genai
from typing import Dict, Any, List
import json  # For handling JSON data if your agent produces chart data
from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    APIRouter,
)
from pydantic import BaseModel
from google.genai.types import Part, Content
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from datetime import date, datetime
import os
from pymongo import MongoClient

load_dotenv()  # This loads variables from .env into the environment
MONGODB_URL = os.getenv("MONGODB_URL")


if not MONGODB_URL:
    raise EnvironmentError("Environment variable MONGODB_URL not set in .env")


def get_few_users_from_sample_analytics(limit=5):
    """Fetch a few documents from the customers collection in sample_analytics as plain dictionaries."""
    client = MongoClient(MONGODB_URL)
    db = client.sample_analytics
    customers = db.customers

    documents = []
    for doc in customers.find().limit(limit):
        doc["_id"] = str(doc["_id"])  # convert ObjectId to str
        documents.append(doc)
    return documents


query_planner_agent = LlmAgent(
    name="query_planner_agent",
    model="gemini-2.0-flash",
    description="plans the mongodb query as per user questions",
    instruction="""
        You are a query planning specialist for MongoDB analytics. Your job is to analyze user questions about the sample_analytics database and create a detailed execution plan.
        The database contains three collections with nested structures:

        accounts: Contains account_id, limit, and products (array)
        customers: Contains username, name, address, birthdate (date object), email, accounts (array), and tier_and_details (nested object with dynamic keys containing tier, benefits array, active status, and id)
        transactions: Contains account_id, transaction_count, bucket dates (date objects), and transactions (array of objects with date, amount, transaction_code, symbol, price, total)

        Pay special attention to nested fields like tier_and_details objects, transaction arrays, and MongoDB date formats when planning queries.
        Query Validation: Before creating a plan, check if the user's question is:

        Ambiguous: If the question is unclear or could have multiple interpretations, ask for clarification
        Impossible: If the requested data doesn't exist in the database schema, explain what's available instead
        Invalid: If the query asks for operations that don't make sense (e.g., mathematical operations on text fields)

        When you receive a user question, analyze what type of query it is (definition, filter, aggregation, trend analysis, comparison, etc.) and break it down into clear steps. Consider which collections need to be accessed, what fields are required, whether joins are needed, what aggregation operations might be necessary, and how to handle nested structures.
        For nested fields, specify:

        How to access tier_and_details with dynamic keys
        How to query within transactions arrays
        How to handle date objects and date range queries
        When to use $unwind for arrays or $elemMatch for array elements

        Create a step-by-step plan that explains:

        Which collections to query
        What fields to extract or filter on
        What aggregation operations are needed
        How to structure the MongoDB query
        Expected output format

        If the query is impossible or ambiguous, explain the issue and suggest alternatives. Your plan should be detailed enough for the next agent to build the actual MongoDB query.
    """,
    output_key="plan",
)

query_builder_agent = LlmAgent(
    name="query_builder_agent",
    model="gemini-2.0-flash",
    description="Connects to MongoDB and retrieves data based on user queries",
    instruction="""
        You are a Python MongoDB query construction specialist. You receive a detailed plan {plan} from the query planner and build actual Python code using PyMongo to execute against the MongoDB cluster.
        Use the {plan} that contains the execution strategy from the previous agent. You have access to UnsafeLocalCodeExecutor to run Python code that connects to the MongoDB cluster.
        The MongoDB connection URL is stored in the environment variable MONGODB_URL. Use PyMongo library to connect to the sample_analytics database and execute queries on the accounts, customers, and transactions collections.
        Based on the plan, write complete Python code using PyMongo syntax that:

        Imports necessary libraries (pymongo, os, datetime, etc.)
        Connects to MongoDB using: client = pymongo.MongoClient(os.getenv('MONGODB_URL'))
        Accesses the database: db = client.sample_analytics
        Uses PyMongo methods like db.collection.find(), db.collection.aggregate(), etc.
        Handles nested fields like tier_and_details objects, transactions arrays, and date objects
        Uses appropriate PyMongo operators and syntax (not JavaScript MongoDB syntax)
        Converts results to Python lists/dicts using list(cursor) when needed
        Includes proper error handling with try/except blocks
        Validates the plan is executable before attempting the query
        Prints the results
        Shows the actual count and sample of results for debugging

        Error Handling: Your code must handle:

        Connection failures: MongoDB connection issues
        Invalid queries: Malformed aggregation pipelines or query syntax
        Empty results: When no data matches the criteria
        Plan execution issues: If the plan from the previous agent is unclear or impossible to implement

        If the plan cannot be executed, set database_results to an error message explaining the issue and suggest what information is actually available.
        Write the complete Python code first, then immediately execute it using UnsafeLocalCodeExecutor. Make sure your code actually runs and produces real results from the MongoDB database. If there are errors, fix them and re-execute. Do NOT just return empty results or "```". The database_results variable from your successful code execution will be passed to the next agent.
        Example structure:
        pythonimport pymongo
        import os

        try:
            client = pymongo.MongoClient(os.getenv('MONGODB_URL'))
            db = client.sample_analytics
            
            # Your query logic here based on the plan
            results = list(db.customers.find(...))  # or aggregate
            
            database_results = results
            print(f"Found {len(results)} results")
            if results:
                print("Sample result:", results[0])
                
        except Exception as e:
            print(f"Error: {e}")
            database_results = []
            
        **you must use code executor if there is a valid plan, if there is an error. you may pass it on to next agent directly repeating the issues discused in {plan} **
    """,
    code_executor=UnsafeLocalCodeExecutor(),
    output_key="database_results",
)

query_answerer_agent = LlmAgent(
    name="query_answerer_agent",
    model="gemini-2.0-flash",
    description="Provides natural language responses based on database query results",
    instruction="""
        You are a data analyst who interprets MongoDB query results and provides clear, user-friendly answers.
        You receive the {database_results} variable from the query builder agent containing the raw MongoDB query output. Your job is to analyze these results and provide a comprehensive answer to the original user question.
        Error Handling: First check if {database_results} contains:

        Error messages: If the previous agent encountered issues, explain the problem and suggest alternatives
        Empty results: If no data was found, explain why and suggest related queries that might have data
        Invalid data: If the results seem incorrect or malformed, point this out

        Transform valid database results into:

        Clear, natural language explanations
        Relevant insights and patterns
        Formatted data presentations when appropriate
        Summary statistics or key findings
        Visual descriptions of trends or relationships

        Query Validation: If the original query was problematic:

        Explain what went wrong (ambiguous request, missing data, impossible operation)
        Suggest what information is actually available in the database
        Offer alternative queries that could provide useful insights

        Make your response accessible to users who may not be familiar with database structures. Focus on answering their original question directly while highlighting any interesting insights found in the data.
        If the results indicate technical issues (connection problems, query errors), explain these in simple terms and suggest next steps.
    """,
    output_key="response",
)

ROOT_AGENT = SequentialAgent(
    name="orchestratorAgent",
    # Run parallel research first, then merge
    sub_agents=[query_planner_agent, query_builder_agent, query_answerer_agent],
    description="this is start of every conversation, it handles the sequence of agents for fetching data from mongodb and then answering user query",
)


agent = ROOT_AGENT

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

APP_NAME = "SylvrDemo"

global_runner = Runner(
    app_name=APP_NAME,
    agent=ROOT_AGENT,
    session_service=session_service,
    artifact_service=artifact_service,  # If your agents use it, pass it here too
)


# Your Pydantic model for the response (I've added this for completeness)
class AgentResponse(BaseModel):
    session_id: str
    summary: str


# 1. Create the main FastAPI application instance
app = FastAPI()

chat = APIRouter()


@chat.websocket("/chat")
async def websocket_chat(
    websocket: WebSocket,
):
    try:
        await websocket.accept()

        # sample_users = get_few_users_from_sample_analytics(limit=5)

        initial_state = {
            # "user_data_example": sample_users
        }

        session_id = str(uuid.uuid4())

        session = session_service.create_session(
            app_name=APP_NAME,
            user_id=session_id,
            session_id=session_id,
            state=initial_state,
        )
        summary = {}
        updated_session = session_service.get_session(
            app_name=APP_NAME, user_id=session.user_id, session_id=session_id
        )
        summary = updated_session.state
        print(summary)
        summary = ""
        final_output = ""

        while True:
            try:
                # print(f"User input for session {session_id}: {user_input.message}")
                raw_data = await websocket.receive_text()
                if not raw_data.strip():
                    print("⚠️ Empty message received, skipping...")
                    continue  # Skip if the message is empty.
                data = json.loads(raw_data)
                message = data.get("message")
                print(f"User input for session {session_id}: {message}")
                events = global_runner.run_async(
                    session_id=session_id,  # Use the actual session ID from the created/retrieved session
                    user_id=session.user_id,  # Use the actual user ID
                    new_message=Content(
                        role="user", parts=[Part.from_text(text=message)]
                    ),
                    run_config=RunConfig(response_modalities=["TEXT"]),
                )

                full_response = ""
                final_text = ""
                async for event in events:
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                print(part.text, end="", flush=True)
                                full_response += part.text
                    if not event.partial:
                        print("\n\n📨 Final Response:\n")
                        pprint.pprint(full_response.strip())
                        final_text = ""

                    # print(final_text)
                updated_session = session_service.get_session(
                    app_name=APP_NAME, user_id=session.user_id, session_id=session_id
                )

                session_state_dict = updated_session.state
                print(
                    f"DEBUG: Full session state for session {session_id} after run: {session_state_dict}"
                )  # For debugging

                if updated_session is None:
                    raise HTTPException(status_code=404, detail="Session not found")

                # output = session_state_dict["response"]
                output = session_state_dict["response"]

                print("-------------------\n")
                print("\n\nFinal output : ", final_output)
                response = AgentResponse(
                    session_id=session_id,
                    # response=full_response_text,  # Clean up any extra whitespace
                    # session_dict=session_state_dict,
                    # summary=full_response,
                    summary=output,
                )
                print("\n\n\n#########FULL CONVERSATION###########\n\n")
                print(full_response)

                # print("Sending response to user", response)

                # Send the response back to the client
                await websocket.send_json(response.model_dump(mode="json"))

            except json.JSONDecodeError:
                await websocket.send_text(
                    "Error: Invalid JSON format. Please send a valid JSON message."
                )
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
    except Exception as e:
        print("Error in creating chat session :", e)


app.include_router(chat)
