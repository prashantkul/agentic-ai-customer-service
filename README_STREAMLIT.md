# Streamlit App Refactoring Guide

The Streamlit application has been refactored to improve maintainability and organization. This document explains the refactored structure and how to use it.

## Structure Overview

The code is now organized into modular components:

```
streamlit_components/
├── __init__.py       # Package initialization
├── agent.py          # Agent interaction logic
├── cart.py           # Cart display and management
├── chat.py           # Chat interface functions
├── config.py         # Configuration settings
├── debug.py          # Debug tools 
├── order.py          # Order submission process
└── utils.py          # Utility functions
```

## Main Components

### 1. Utils (`utils.py`)
Contains utility functions used throughout the application:
- `call_agent_api`: Makes API calls to the agent
- `parse_sse_response`: Parses Server-Sent Events responses
- `update_cart_display`: Updates the cart in session state

### 2. Cart Management (`cart.py`) 
Handles display and management of the shopping cart:
- `display_cart`: Shows the cart contents
- `display_cart_total`: Calculates and shows the cart total
- `display_order_confirmation`: Shows confirmation after order submission

### 3. Chat Interface (`chat.py`)
Manages the chat interface functionality:
- `display_chat_messages`: Shows the conversation history
- `handle_user_input`: Processes new user messages
- `is_cart_related_query`: Determines if a query relates to cart/ordering

### 4. Order Processing (`order.py`)
Handles the order submission workflow:
- `display_action_buttons`: Shows the cart action buttons
- `display_order_confirmation_dialog`: Shows order confirmation dialog
- `display_standard_buttons`: Shows standard cart action buttons

### 5. Agent Interaction (`agent.py`)
Manages communication with the agent:
- `process_agent_interaction`: Main function to interact with the agent
- `ensure_agent_session`: Ensures an agent session exists
- `format_effective_prompt`: Formats prompts for specific actions
- `handle_cart_information`: Processes cart information from agent
- `explicitly_fetch_cart`: Makes explicit cart information requests

### 6. Configuration (`config.py`)
Contains application configuration settings:
- API endpoints
- Environment variables
- Logging setup

### 7. Debug Tools (`debug.py`)
Provides debugging utilities:
- `display_debug_section`: Shows debugging options and information

## Main Application

The main application file (`streamlit_app_refactored.py`) integrates all components:
1. Imports components from the modular structure
2. Sets up the page configuration and header
3. Initializes session state variables
4. Creates the main layout with chat and sidebar columns
5. Delegates functionality to the appropriate components

## Usage

To run the refactored Streamlit app:

```bash
streamlit run streamlit_app_refactored.py
```

## Benefits of Refactoring

- **Improved Maintainability**: Each component has a single responsibility
- **Better Organization**: Related functions are grouped together
- **Easier Debugging**: Isolated components are easier to debug
- **Simplified Main App**: The main app file is much shorter and clearer
- **Reusability**: Components can be reused in other parts of the application
- **Collaborative Development**: Different team members can work on different components

## Extending the Application

To add new features:
1. Determine which component the feature belongs to (or create a new one)
2. Implement the feature in the appropriate component
3. Update the main application to use the new functionality