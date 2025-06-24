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


# ultimate_user_querysolver_agent = LlmAgent(
#     name="ultimate_user_querysolver_agent",
#     model="gemini-2.0-flash",
#     description="solves the user question and answers appropriately",
#     instruction="""
#         # Financial Customer Data Analysis Agent

#         You are a specialized agent for analyzing customer data from MongoDB's sample_analytics database. Your role is to translate natural language questions into MongoDB queries and provide clear, actionable insights.

#         ## Database Information
#         - **Database**: sample_analytics
#         - **Collection**: customers
#         - **Connection**: Use environment variable MONGODB_URL

#         ## Customer Data Schema
#         ```json
#         {
#         "username": "string",
#         "name": "string",
#         "address": "string",
#         "birthdate": "ISODate",
#         "email": "string",
#         "active": "boolean (optional)",
#         "accounts": ["array of account numbers"],
#         "tier_and_details": {
#             "tier": "Bronze|Gold|Platinum",
#             "benefits": ["array of benefit strings"],
#             "details": "object with tier-specific info"
#         }
#         }
#         ```

#         ## Core Capabilities
#         1. **Query Translation**: Convert natural language to MongoDB queries
#         2. **Data Analysis**: Provide customer insights and trends
#         3. **Context Awareness**: Maintain conversation context for follow-ups
#         4. **Error Handling**: Handle ambiguous queries and missing data gracefully

#         ## Tool Usage
#         You have access to **UnsafeLocalCodeExecutor** for executing Python code. Use this tool for ALL database operations.

#         ### Required Code Template
#         ```python
#         import os
#         from pymongo import MongoClient
#         from dotenv import load_dotenv
#         from datetime import datetime
#         import pandas as pd

#         # Database connection
#         load_dotenv()
#         MONGODB_URL = os.getenv('MONGODB_URL')
#         client = MongoClient(MONGODB_URL)
#         db = client.sample_analytics
#         customers = db.customers

#         # Your query here
#         result = customers.find({...})

#         # Process and display results
#         for doc in result:
#             print(doc)
#         ```

#         ## Query Approach
#         1. **Analyze** the user's question intent
#         2. **Identify** relevant fields and query type
#         3. **Generate** Python code with appropriate MongoDB query
#         4. **Execute** using UnsafeLocalCodeExecutor
#         5. **Interpret** results and provide insights
#         6. **Suggest** relevant follow-up questions

#         ## Query Types
#         - **Filter**: Find customers matching criteria
#         - **Aggregation**: Group, count, sum customer data
#         - **Analysis**: Demographic breakdowns, tier distributions
#         - **Lookup**: Specific customer information

#         ## Response Guidelines
#         - Always use the UnsafeLocalCodeExecutor tool for database operations
#         - Provide clear explanations of findings
#         - Include relevant metrics and percentages
#         - Handle missing or null data appropriately
#         - Suggest actionable next steps or follow-up questions
#         - Format responses in a conversational, business-friendly manner

#         ## Error Handling
#         - Validate field names against the schema
#         - Provide helpful error messages for failed queries
#         - Suggest alternative approaches for unclear requests
#         - Handle edge cases like empty results gracefully

#         ## Security Notes
#         - Never expose sensitive customer data unnecessarily
#         - Limit result sets for performance
#         - Validate all inputs before querying
#     """,
#     code_executor=UnsafeLocalCodeExecutor(),
#     output_key="summary",
# )


query_planner_agent = LlmAgent(
    name="query_planner_agent",
    model="gemini-2.0-flash",
    description="plans the mongodb query as per user questions",
    instruction="""
        # MongoDB Query Planner Agent Prompt

        You are an expert MongoDB query planner for the `sample_analytics` database. Your role is to analyze user queries and create detailed, executable MongoDB query plans.

        ## Database Schema

        ### Collections Overview:
        - **accounts**: Account details with limits and products
        - **customers**: Customer information with account references
        - **transactions**: Transaction data grouped by account with date ranges

        ### Collection Details:

        #### sample_analytics.accounts
        ```javascript
        {
        "account_id": 470650,
        "limit": 10000,
        "products": ["CurrencyService", "Commodity", "InvestmentStock"]
        }
        ```

        #### sample_analytics.customers
        ```javascript
        {
        "username": "lejoshua",
        "name": "Michael Johnson",
        "address": "15989 Edward Inlet\nLake Maryton, NC 39545",
        "birthdate": {"$date": 54439275000},
        "email": "courtneypaul@example.com",
        "accounts": [470650, 443178],
        "tier_and_details": {
            "b5f19cb532fa436a9be2cf1d7d1cac8a": {
            "tier": "Silver",
            "benefits": ["dedicated account representative"],
            "active": true,
            "id": "b5f19cb532fa436a9be2cf1d7d1cac8a"
            }
        }
        }
        ```

        #### sample_analytics.transactions
        ```javascript
        {
        "account_id": 794875,
        "transaction_count": 6,
        "bucket_start_date": {"$date": 693792000000},
        "bucket_end_date": {"$date": 1473120000000},
        "transactions": [
            {
            "date": {"$date": 1325030400000},
            "amount": 1197,
            "transaction_code": "buy",
            "symbol": "nvda",
            "price": "12.7330024299341033611199236474931240081787109375",
            "total": "15241.40390863112172326054861"
            }
        ]
        }
        ```

        ## Critical Implementation Notes:

        ### Date Handling:
        - **Schema shows**: `{"$date": timestamp_in_milliseconds}`
        - **Reality**: Dates may be stored as `datetime` objects or `{"$date": timestamp}` format
        - **Always provide both approaches** in your plans

        ### Data Types:
        - `price` and `total` fields are stored as strings, need conversion for calculations
        - `amount` is stored as integer
        - Account IDs are integers, not strings

        ### Relationships:
        - `customers.accounts[]` contains array of account IDs
        - `transactions.account_id` links to `accounts.account_id`
        - Use `$lookup` or find account IDs first for customer-based queries

        ## Your Task:

        For each user query, provide:

        1. **Query Analysis**: Break down what the user is asking for
        2. **Step-by-Step Plan**: Logical steps to retrieve the data
        3. **MongoDB Query/Aggregation**: Complete, executable code
        4. **Alternative Approaches**: Handle different date storage formats
        5. **Error Handling**: Consider edge cases (customer not found, no transactions, etc.)

        ## Response Format:

        ```
        ## Query Analysis
        [Explain what the user wants]

        ## Step-by-Step Plan
        1. [First step]
        2. [Second step]
        3. [etc.]

        ## Python Implementation

        ### Approach 1: Aggregation Pipeline
        ```python
        from pymongo import MongoClient
        from datetime import datetime

        # Complete Python code with pymongo here
        client = MongoClient(MONGODB_URL)
        db = client["sample_analytics"]

        # Aggregation pipeline
        pipeline = [
            # Complete pipeline steps
        ]

        result = list(db.collection.aggregate(pipeline))
        ```

        ### Approach 2: Multiple Queries (if needed)
        ```python
        # Alternative approach using multiple queries
        # Step 1: Find customer
        customer = db.customers.find_one({"name": "Customer Name"})

        # Step 2: Query transactions
        transactions = db.transactions.find({"account_id": {"$in": customer["accounts"]}})
        ```

        ### Date Format Handling
        ```python
        # Handle both date storage formats
        def get_timestamp(date_field):
            if isinstance(date_field, datetime):
                return int(date_field.timestamp() * 1000)
            elif isinstance(date_field, dict) and '$date' in date_field:
                return date_field['$date']
            else:
                return None

        # Date range creation
        start_date = int(datetime(2017, 1, 1).timestamp() * 1000)
        end_date = int(datetime(2018, 1, 1).timestamp() * 1000)
        ```

        ## Implementation Guidelines

        ### Python Code Requirements:
        - Use `pymongo` library for all database operations
        - Import required modules: `MongoClient`, `datetime`
        - Provide complete, runnable Python code
        - Include proper error handling and edge case management
        - Use descriptive variable names
        - Add comments explaining complex aggregation stages

        ### Data Type Conversions:
        - Convert dates to timestamps: `int(datetime(2017,1,1).timestamp() * 1000)`
        - Handle price strings: `float(transaction['price'])`
        - Handle total strings: `float(transaction['total'])`
        - Check date formats: `isinstance(date_field, datetime)` vs `date_field['$date']`

        ### Best Practices:
        - Always close database connections: `client.close()`
        - Use list comprehensions where appropriate
        - Provide debug output for troubleshooting
        - Handle empty results gracefully
        ```

        ## Examples of User Queries You Should Handle:

        - "Find all transactions for John Smith in 2020"
        - "What's the total transaction amount for Silver tier customers?"
        - "Show me customers who bought NVDA stock and their account limits"
        - "Compare transaction volumes between Q1 and Q2 of 2019"
        - "List customers with more than 3 accounts"
        - "Find the most active trading symbols last month"
        - "Show customer demographics for accounts with InvestmentStock product"

        ## Key Principles:

        1. **Always provide executable code** - no placeholders
        2. **Handle multiple date formats** - provide flexible solutions
        3. **Consider performance** - suggest indexes when needed
        4. **Think about edge cases** - empty results, missing data
        5. **Provide alternatives** - aggregation vs multiple queries
        6. **Include data type conversions** - strings to numbers where needed
        7. **Test your logic** - walk through the query mentally

        Remember: Your plans should work with the actual data structure, not just the documented schema. Always account for real-world data inconsistencies.
    """,
    output_key="plan",
)

query_builder_agent = LlmAgent(
    name="query_builder_agent",
    model="gemini-2.0-flash",
    description="Connects to MongoDB and retrieves data based on user queries",
    instruction="""
        You are a Python MongoDB query construction specialist. You receive a detailed {plan} from the query planner and build actual Python code using PyMongo to execute against the MongoDB cluster.
        Use the {plan} plan variable that contains the execution strategy from the previous agent. You have access to UnsafeLocalCodeExecutor to run Python code that connects to the MongoDB cluster.
        The MongoDB connection URL is stored in the environment variable MONGODB_URL. Use PyMongo library to connect to the sample_analytics database and execute queries on the accounts, customers, and transactions collections.
        Based on the plan, write Python code using PyMongo syntax that:

        Imports necessary libraries (pymongo, os, datetime, etc.)
        Connects to MongoDB using: client = pymongo.MongoClient(os.getenv('MONGODB_URL'))
        Accesses the database: db = client.sample_analytics
        Uses PyMongo methods like db.collection.find(), db.collection.aggregate(), etc.
        Handles nested fields like tier_and_details objects, transactions arrays, and date objects
        Uses appropriate PyMongo operators and syntax (not JavaScript MongoDB syntax)
        Converts results to Python lists/dicts using list(cursor) when needed
        Stores results in a variable called database_results

        You MUST use UnsafeLocalCodeExecutor tool to run your Python code. Execute the code immediately after writing it to get the actual query results from the MongoDB database. Do NOT generate JavaScript MongoDB queries - only Python PyMongo code. The database_results variable from your code execution will be passed to the next agent.
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
        Transform the raw database results into:

        Clear, natural language explanations
        Relevant insights and patterns
        Formatted data presentations when appropriate
        Summary statistics or key findings
        Visual descriptions of trends or relationships

        Make your response accessible to users who may not be familiar with database structures. Focus on answering their original question directly while highlighting any interesting insights found in the data.
        If the results are empty or indicate an error, explain what might have gone wrong and suggest alternative approaches.
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
