# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Agent module for the customer service agent with database integration."""

import logging
import warnings
from google.adk import Agent
from .config import Config
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from .shared_libraries.callbacks import (
    rate_limit_callback,
    before_agent,
    before_tool,
)

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()

# configure logging __name__
logger = logging.getLogger(__name__)


# Try to import database-backed tools first, but fall back to mock tools if needed
try:
    # Import database-backed tools
    from .database.db_tools import (
        send_call_companion_link,
        approve_discount,
        sync_ask_for_approval,
        update_salesforce_crm,
        access_cart_information,
        modify_cart,
        get_product_recommendations,
        check_product_availability,
        schedule_service,
        get_available_service_times,
        send_training_tips,
        generate_qr_code,
    )

    # Initialize the database (if not already initialized)
    try:
        from .database.init_db import init_db, ensure_tables_exist

        # Only ensure tables exist without clearing data
        ensure_tables_exist()
        logger.info("Database tables initialized successfully (without clearing data)")
        using_database = True
    except Exception as e:
        logger.warning(f"Failed to initialize database: {e}")
        using_database = False

except ImportError:
    # Fall back to mock tools
    logger.warning("Database tools not available, using mock tools")
    from .tools.tools import (
        send_call_companion_link,
        approve_discount,
        sync_ask_for_approval,
        update_salesforce_crm,
        access_cart_information,
        modify_cart,
        get_product_recommendations,
        check_product_availability,
        schedule_service,
        get_available_service_times,
        send_training_tips,
        generate_qr_code,
    )

    using_database = False

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()

# configure logging __name__
logger = logging.getLogger(__name__)

# Log whether we're using database or mock tools
logger.info(f"Using database-backed tools: {using_database}")

root_agent = Agent(
    model=configs.agent_settings.model,
    global_instruction=GLOBAL_INSTRUCTION,
    instruction=INSTRUCTION,
    name=configs.agent_settings.name,
    tools=[
        send_call_companion_link,
        approve_discount,
        sync_ask_for_approval,
        update_salesforce_crm,
        access_cart_information,
        modify_cart,
        get_product_recommendations,
        check_product_availability,
        schedule_service, 
        get_available_service_times,  
        send_training_tips,  
        generate_qr_code,
    ],
    before_tool_callback=before_tool,
    before_agent_callback=before_agent,
    before_model_callback=rate_limit_callback,
)
