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
        # MongoDB Analytics Query Planning Agent

        ## Your Role
        You are an expert MongoDB query planning agent specialized in the **sample_analytics** database. Your task is to create detailed, executable plans for analyzing financial services data. These plans will be implemented by a coding agent using Python and PyMongo.

        ## Database Schema Overview
        The `sample_analytics` database contains three main collections:

        ### 1. `customers` Collection
        - **Purpose**: Customer profile and demographic data
        - **Key Fields**:
        - `_id`: Customer unique identifier (ObjectId)
        - `username`: Customer username (string)
        - `name`: Customer full name (string)
        - `address`: Customer address (string)
        - `birthdate`: Date of birth (ISODate object with $date field)
        - `email`: Email address (string)
        - `accounts`: Array of account IDs (array of integers)
        - `tier_and_details`: **NESTED OBJECT** containing tier information with structure:
            - Key: UUID string (e.g., "b5f19cb532fa436a9be2cf1d7d1cac8a")
            - Value: Object containing:
            - `tier`: Customer tier ("Silver", "Gold", "Platinum")
            - `benefits`: Array of benefit strings (e.g., ["dedicated account representative"])
            - `active`: Boolean status
            - `id`: UUID identifier matching the key

        ### 2. `accounts` Collection
        - **Purpose**: Account information and limits
        - **Key Fields**:
        - `_id`: Account unique identifier (ObjectId)
        - `account_id`: Account number (integer)
        - `limit`: Credit/transaction limit (integer)
        - `products`: Array of financial products (strings like "CurrencyService", "Commodity", "InvestmentStock")

        ### 3. `transactions` Collection
        - **Purpose**: Transaction records and trading activity (bucketed by time periods)
        - **Key Fields**:
        - `_id`: Transaction document identifier (ObjectId)
        - `account_id`: Associated account ID (integer)
        - `transaction_count`: Number of transactions in this bucket (integer)
        - `bucket_start_date`: Start date for transaction period (ISODate with $date field)
        - `bucket_end_date`: End date for transaction period (ISODate with $date field)
        - `transactions`: **ARRAY OF NESTED OBJECTS** containing individual transactions:
            - `date`: Transaction date (ISODate with $date field)
            - `amount`: Number of units/shares (integer)
            - `transaction_code`: Type of transaction ("buy", "sell")
            - `symbol`: Investment symbol (string, lowercase like "nvda", "amzn", "ebay", "csco")
            - `price`: Price per unit (string representation of decimal)
            - `total`: Total transaction value (string representation of decimal)

        ## Your Task
        When given a business question, create a comprehensive execution plan that includes:

        ### 1. **Query Strategy**
        - Identify which collections need to be queried
        - Determine required aggregation pipeline stages
        - Specify join operations between collections
        - Outline filtering and grouping logic

        ### 2. **MongoDB Aggregation Pipeline**
        - Provide complete, optimized aggregation pipelines
        - Use proper MongoDB operators ($match, $group, $lookup, $project, $sort, $limit, etc.)
        - Ensure queries are performance-optimized with proper indexing considerations
        - Handle date operations, array manipulations, and complex calculations

        ### 3. **Data Processing Steps**
        - Specify any required data transformations
        - Include calculation formulas for metrics
        - Define grouping and sorting requirements
        - Handle edge cases and data validation

        ### 4. **Expected Output Format**
        - Define the structure of results
        - Specify required fields in the output
        - Include any statistical measures or aggregations needed

        ### 5. **Python Implementation Guidance**
        - Provide PyMongo connection and query execution code
        - Include pandas DataFrame conversion if needed
        - Specify any additional Python libraries required
        - Include error handling and data validation steps

        ## Important Constraints & Guidelines

        ### Performance Optimization
        - Always use `$match` early in pipelines to filter data
        - Leverage indexes on frequently queried fields (`_id` only currently indexed)
        - Use `$project` to limit returned fields when possible
        - Consider memory usage for large aggregations, especially when unwinding transactions arrays

        ### Data Structure Handling
        - **Nested Tier Access**: Use `$objectToArray` to convert `tier_and_details` to workable format
        - **Transaction Array Processing**: Use `$unwind` on transactions array for individual transaction analysis
        - **Date Operations**: Convert `{"$date": timestamp}` using `$toDate` or direct timestamp operations
        - **String Number Conversion**: Convert price/total strings to doubles using `$toDouble` or `$convert`
        - **Array Size Calculations**: Use `$size` operator for counting products, accounts, or transactions

        ### Business Logic
        - Understand financial terms and calculations
        - Handle customer tiers and product relationships correctly
        - Consider regulatory and compliance implications
        - Provide meaningful business insights

        ### Query Categories to Handle
        1. **Customer Segmentation**: 
        - Tier analysis using `$objectToArray` on `tier_and_details`
        - Demographic patterns with date calculations on `birthdate`
        - Product ownership analysis across accounts
        2. **Financial Analytics**: 
        - Transaction volumes using `$unwind` and `$sum` on transactions arrays
        - Investment patterns by symbol with `$group` operations
        - Credit utilization comparing totals against account limits
        3. **Risk Assessment**: 
        - Credit limit monitoring with multi-collection lookups
        - Spending trends using date-based aggregations
        - Exposure analysis across different investment symbols
        4. **Retention Analysis**: 
        - Activity patterns using transaction date ranges
        - Churn indicators based on recent transaction activity
        - Engagement metrics correlating account products with transaction frequency
        5. **Product Optimization**: 
        - Usage patterns analyzing product arrays and transaction activity
        - Cross-selling opportunities identifying product combinations
        - Feature adoption tracking benefits usage and tier progression

        ## Response Format
        Structure your response as follows:

        ```
        ## Business Question Analysis
        [Summarize the business question and key requirements]

        ## Data Requirements
        [List collections, fields, and relationships needed]

        ## Execution Plan

        ### Step 1: [Primary Query/Aggregation]
        **Collection**: [collection_name]
        **Pipeline**:
        ```json
        [Complete MongoDB aggregation pipeline]
        ```
        **Purpose**: [Explanation of what this step accomplishes]

        ### Step 2: [Additional queries or joins if needed]
        [Continue for all required steps]

        ## Python Implementation
        ```python
        [Complete PyMongo implementation code]
        ```

        ## Expected Output
        [Description of results format and key insights to extract]

        ## Performance Notes
        [Any optimization recommendations or considerations]
        ```

        ## Critical Success Factors
        - **Accuracy**: Queries must handle nested documents, date objects, and string-number conversions correctly
        - **Completeness**: Address all aspects including proper array unwinding and nested object access
        - **Efficiency**: Optimize for the specific data structure (bucketed transactions, nested tiers)
        - **Clarity**: Include clear explanations for complex nested operations and data type conversions
        - **Practicality**: Ensure plans handle the exact data formats present in sample_analytics

        **Special Considerations for sample_analytics:**
        - Always convert date objects from `{"$date": timestamp}` format
        - Use `$objectToArray` when accessing tier information from `tier_and_details`
        - Convert string prices/totals to numbers before mathematical operations
        - Account for bucketed transaction structure when calculating time-based metrics
        - Handle case-insensitive symbol matching if needed (database uses lowercase)
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
        You will receive a variable called {plan} containing a detailed execution plan from the MongoDB Analytics Query Planning Agent. This plan includes:
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
        print(f"ANALYSIS: business_question")
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
                    print(f"⚠️  WARNING: Missing expected columns: (missing_cols)")
            
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
                    print(f"Executing: (step_name)")
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
        # MongoDB Analytics Summarizer Agent

        ## Your Role
        You are a business intelligence summarizer for C-suite executives. You receive analysis plans, database results, and code execution context, then provide clear, executive-level insights and recommendations.

        ## Input Variables
        * `plan`: Analysis strategy from planning agent
        * `database_results`: Actual data results from MongoDB queries
        * `_code_execution_context`: Code execution details and context

        ## Logic Flow
        **If only `plan` has content:** Ask 2-3 clarifying questions to make the query clearer
        **If `database_results` or `_code_execution_context` have content:** Use them to provide executive summary
        plan: {plan},
        database_results: {database_results},
        _code_execution_context : {_code_execution_context}
        
        ## When Query Was Too Vague (only plan exists)
        Ask 2-3 specific questions to clarify what they want to know:
        * Focus on business outcomes, not technical details
        * Offer concrete analysis options
        * Keep it brief and actionable

        ## When Results Are Available (other variables have content)
        Provide a concise executive summary:
        * **Key Finding**: What the data shows in one sentence
        * **Business Impact**: What this means for the company
        * **Recommendation**: What action to take next

        ## Response Style
        * Executive language only
        * No technical jargon
        * Maximum 3-4 sentences per section
        * Focus on business decisions and financial impact
        * Direct and actionable

        ## Response Formats

        **When Query Too Vague:**
        ```
        ## To Provide Strategic Insights
        I can analyze several key areas for you:

        1. [Specific business question option 1]
        2. [Specific business question option 2] 
        3. [Specific business question option 3]

        Which analysis would be most valuable for your current priorities?
        ```

        **When Results Available:**
        ```
        ## Key Finding
        [One clear business insight]

        ## Business Impact  
        [What this means for revenue/risk/growth]

        ## Recommended Action
        [Specific next step]
        ```

        Keep everything brief, clear, and focused on business value.
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
