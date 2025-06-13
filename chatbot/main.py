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
MONGODB_URI = os.getenv("MONGODB_URI")


if not MONGODB_URI:
    raise EnvironmentError("Environment variable MONGODB_URI not set in .env")


def get_few_users_from_sample_analytics(limit=5):
    """Fetch a few documents from the customers collection in sample_analytics as plain dictionaries."""
    client = MongoClient(MONGODB_URI)
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
        Role: Analyze user questions and plan what data to get.
        What you do:

        Read the user's question
        Look at the {user_data_example} provided in context
        Identify query type and plan approach
        Tell Agent 2 what to execute

        Query Types to Handle:

        Definitions: "What is X?" - Get field descriptions, counts, examples
        Filters: "Show me users who..." - Filter by conditions, nested field matching
        Aggregations: "How many/average/total..." - Count, sum, average, group operations
        Trends: "Over time/by age/by tier..." - Group by time periods, demographics, tiers
        Comparisons: "Compare X vs Y" - Side-by-side analysis, differences, ratios

        For nested data planning:

        Identify if nested objects need flattening (tier_and_details, benefits arrays)
        Plan aggregation pipelines for complex nested structures
        Consider empty nested objects in your planning
        Plan for dynamic object keys that vary per document

        Output: Simple plan with query type, required operations, and processing steps.
    """,
    output_key="plan",
)

query_builder_agent = LlmAgent(
    name="query_builder_agent",
    model="gemini-2.0-flash",
    description="Connects to MongoDB and retrieves data based on user queries",
    instruction="""
        Role: Connect to database and get the data.
        What you do:
        
        load {plan}
        FIRST: Load MONGODB_URI from .env file - Always read environment variables
        Connect to MongoDB using the MONGODB_URI from .env
        Execute based on query type from Agent 1
        Process the results appropriately
        Handle any errors
        Return clean data to Agent 3

        Database Connection:

        Read .env file to get MONGODB_URI
        Use MONGODB_URI environment variable for connection
        Connect to the 'sample_analytics' collection
        Handle connection errors if .env or URI is missing

        Execution by Query Type:

        Definitions: Use find() or simple aggregation for samples and field info
        Filters: Use $match with nested field queries when needed
        Aggregations: Use $group, $count, $sum, $avg with proper grouping
        Trends: Use $group with date/demographic fields, $sort for ordering
        Comparisons: Use $facet or multiple aggregations, calculate differences

        For nested data execution:

        Use aggregation pipelines, not simple find() for complex queries
        Convert objects with dynamic keys using $objectToArray
        Use $unwind to process nested arrays and objects
        Handle empty nested objects with preserveNullAndEmptyArrays: true
        Chain multiple pipeline stages for complex nesting

        Important: Always start by loading environment variables. Don't hardcode database connections.
    """,
    code_executor=UnsafeLocalCodeExecutor(),
    output_key="database_results",
)

query_answerer_agent = LlmAgent(
    name="query_answerer_agent",
    model="gemini-2.0-flash",
    description="Provides natural language responses based on database query results",
    instruction="""
        Role: Turn technical results into user-friendly answers.
        What you do:

        read {database_results}
        Answer based on the original query type
        Format appropriately for the question asked
        Suggest follow-ups if helpful

        Response by Query Type:

        Definitions: Explain what fields mean, provide examples, show data structure
        Filters: Present filtered results clearly, mention total counts
        Aggregations: Show numbers with context, percentages, summaries
        Trends: Present patterns, highlight key insights, use time/demographic context
        Comparisons: Show side-by-side results, highlight differences, explain significance

        Keep responses:

        Simple and direct for the query type
        Use business language, not technical terms
        Include relevant numbers and context
        Actionable when appropriate

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

        sample_users = get_few_users_from_sample_analytics(limit=5)

        initial_state = {"user_data_example": sample_users}

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

        # alpha = f"the name of table is {table_name}"
        # # Execute an initial agent query before the main loop
        # initial_query = Content(role="user", parts=[Part.from_text(text=alpha)])

        # Run the agent with the initial query
        # events = global_runner.run_async(
        #     session_id=session_id,
        #     user_id=session.user_id,
        #     new_message=initial_query,
        #     run_config=RunConfig(response_modalities=["TEXT"]),
        # )

        # # Consume the events to ensure the agent processes the query
        # async for event in events:
        #     if event.is_final_response():
        #         print("✅ Message processed successfully.")
        #         break  # Exit after confirming processing

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
