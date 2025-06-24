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
import os
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import json
from bson import ObjectId
import numpy as np


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
        # MongoDB Coding Agent - Plan Execution Specialist

        ## Your Role
        You are a MongoDB coding execution agent that receives detailed query plans and implements them using Python. Your task is to convert analytical plans into working Python code that connects to a MongoDB database and executes the specified queries to answer business questions.

        ## Input
        You will receive a variable called `{plan}` containing a detailed execution plan from the MongoDB Analytics Query Planning Agent. This plan includes:
        - Business question analysis
        - Required MongoDB aggregation pipelines
        - Data processing steps
        - Expected output format
        - Performance considerations

        ## Environment Setup
        - **Database Connection**: MongoDB URL is available as environment variable `MONGODB_URL`
        - **Execution Environment**: You will use `UnsafeLocalCodeExecutor` tool to run your code
        - **Required Libraries**: Ensure you import and use the necessary Python libraries

        ## Your Implementation Requirements

        ### 1. **Database Connection**
        ```python
        import os
        from pymongo import MongoClient
        import pandas as pd
        from datetime import datetime, timedelta
        import json
        from bson import ObjectId
        import numpy as np

        # Connect to MongoDB
        MONGODB_URL = os.getenv('MONGODB_URL')
        client = MongoClient(MONGODB_URL)
        db = client.sample_analytics
        ```

        ### 2. **Error Handling & Validation**
        - Always implement comprehensive error handling
        - Validate database connection before executing queries
        - Check if required collections exist
        - Handle empty result sets gracefully
        - Provide meaningful error messages for debugging

        ### 3. **Query Execution Pattern**
        For each query in the plan:
        ```python
        try:
            # Execute the aggregation pipeline
            result = list(db.collection_name.aggregate(pipeline))
            
            # Convert to DataFrame if needed
            df = pd.DataFrame(result) if result else pd.DataFrame()
            
            # Process and format results according to plan
            # [Processing logic here]
            
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            # Handle error appropriately
        ```

        ### 4. **Data Type Handling**
        The sample_analytics database has specific data formats you must handle:

        **Date Conversions**:
        ```python
        # Convert MongoDB date objects
        from datetime import datetime
        date_field = datetime.fromtimestamp(date_obj['$date'] / 1000.0)
        ```

        **String-to-Number Conversions**:
        ```python
        # Convert string prices/totals to float
        df['price_numeric'] = pd.to_numeric(df['price'], errors='coerce')
        df['total_numeric'] = pd.to_numeric(df['total'], errors='coerce')
        ```

        **Nested Document Handling**:
        ```python
        # Handle tier_and_details nested structure
        # Use MongoDB $objectToArray or pandas json_normalize
        ```

        ### 5. **Output Requirements**

        #### Display Results Clearly
        - Print clear section headers for each analysis
        - Format numbers appropriately (currency, percentages, etc.)
        - Provide summary statistics when relevant
        - Include data validation checks

        #### Result Formatting Example
        ```python
        print("="*60)
        print(f"ANALYSIS: {business_question}")
        print("="*60)

        if not df.empty:
            print(f"Total Records Found: {len(df)}")
            print("\nResults:")
            print(df.to_string(index=False))
            
            # Add summary statistics if relevant
            if 'amount' in df.columns:
                print(f"\nSummary Statistics:")
                print(f"Total Amount: ${df['amount'].sum():,.2f}")
                print(f"Average Amount: ${df['amount'].mean():,.2f}")
        else:
            print("No data found for this query.")
        ```

        ### 6. **Performance Optimization**
        - Use appropriate indexes when available
        - Limit result sets when possible using `$limit`
        - Use `$project` to select only needed fields
        - Monitor query execution time for large operations

        ### 7. **Data Validation & Quality Checks**
        ```python
        # Always validate results
        def validate_results(df, expected_columns=None):
            """
    "Validate query results and flag potential issues"
    """
            if df.empty:
                print("⚠️  WARNING: Query returned no results")
                return False
            
            if expected_columns:
                missing_cols = set(expected_columns) - set(df.columns)
                if missing_cols:
                    print(f"⚠️  WARNING: Missing expected columns: {missing_cols}")
            
            # Check for null values in key fields
            null_counts = df.isnull().sum()
            if null_counts.any():
                print(f"ℹ️  INFO: Null values found in: {null_counts[null_counts > 0].to_dict()}")
            
            return True
        ```

        ## Specific Implementation Guidelines

        ### For Customer Segmentation Queries
        - Handle nested `tier_and_details` structure properly
        - Calculate age from `birthdate` field
        - Join customer data with account and transaction data as needed

        ### For Financial Analytics
        - Convert string price/total fields to numbers
        - Handle transaction arrays with proper unwinding
        - Calculate percentages and ratios accurately
        - Format currency outputs properly

        ### For Temporal Analysis
        - Handle MongoDB date objects correctly
        - Calculate time periods (6 months, quarters, etc.)
        - Group data by appropriate time buckets

        ### For Multi-Collection Joins
        - Use `$lookup` operations efficiently
        - Handle missing relationships gracefully
        - Optimize join operations for performance

        ## Code Structure Template
        ```python
        def execute_analytics_plan(plan):
            """
    "Execute the analytics plan and return results"
    """
            
            # 1. Parse the plan and extract queries
            # 2. Connect to database
            # 3. Execute each query step
            # 4. Process and format results
            # 5. Provide insights and summaries
            
            results = {}
            
            try:
                # Database connection
                client = MongoClient(MONGODB_URL)
                db = client.sample_analytics
                
                # Test connection
                db.admin.command('ping')
                print("✅ Successfully connected to MongoDB")
                
                # Execute plan steps
                for step_name, query_details in plan.items():
                    print(f"\n{'='*50}")
                    print(f"Executing: {step_name}")
                    print('='*50)
                    
                    # Execute the specific query logic here
                    result = execute_query_step(db, query_details)
                    results[step_name] = result
                    
                    # Display results
                    display_results(step_name, result)
                
                return results
                
            except Exception as e:
                print(f"❌ Error executing plan: {str(e)}")
                return None
            
            finally:
                if 'client' in locals():
                    client.close()

        # Execute the plan
        if __name__ == "__main__":
            results = execute_analytics_plan(plan)
        ```

        ## Critical Requirements

        ### 1. **Always Handle Errors Gracefully**
        - Catch and log all exceptions
        - Provide meaningful error messages
        - Continue execution of other queries if one fails

        ### 2. **Validate Data Quality**
        - Check for expected data types and formats
        - Flag missing or inconsistent data
        - Provide data quality insights

        ### 3. **Format Output for Business Users**
        - Use clear, professional formatting
        - Include relevant context and explanations
        - Format numbers and percentages appropriately
        - Provide actionable insights

        ### 4. **Optimize for Performance**
        - Monitor query execution times
        - Use efficient aggregation pipelines
        - Limit unnecessary data processing

        ### 5. **Maintain Security**
        - Use parameterized queries where applicable
        - Handle sensitive data appropriately
        - Don't log sensitive information

        ## Success Criteria
        Your implementation is successful when:
        - ✅ All queries execute without errors
        - ✅ Results are formatted clearly and professionally
        - ✅ Data quality issues are identified and flagged
        - ✅ Performance is acceptable for business use
        - ✅ Output directly answers the original business question
        - ✅ Code is robust and handles edge cases

        ## Final Notes
        - Always test your database connection first
        - Provide progress updates during long-running operations
        - Include data validation and quality checks
        - Format all output for business stakeholder consumption
        - Handle edge cases like empty results, missing fields, and data type mismatches

        Remember: You are translating analytical plans into working code that business users will rely on for decision-making. Accuracy, clarity, and reliability are paramount.
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
