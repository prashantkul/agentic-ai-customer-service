"""
Database-backed agent module for the customer service agent.
"""

import logging
import warnings
from google.adk import Agent
from customer_service.config import Config
from customer_service.prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from customer_service.shared_libraries.callbacks import (
    rate_limit_callback,
    before_agent,
    before_tool,
)
from customer_service.database.db_tools import (
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

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()

# configure logging __name__
logger = logging.getLogger(__name__)


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