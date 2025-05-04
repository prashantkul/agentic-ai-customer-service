# Database-Backed Customer Service Agent

This extension of the BetterSale Sports customer service agent uses a SQLite database to store and retrieve customer data, product information, shopping carts, orders, and service appointments.

## Architecture

The database implementation consists of several components:

1. **Database Models** (`database/models.py`): SQLAlchemy models defining the database schema
2. **Database Operations** (`database/operations.py`): Functions to interact with the database
3. **Database Initialization** (`database/init_db.py`): Script to create and populate the database with sample data
4. **Database-Backed Tools** (`customer_service_db/db_tools.py`): Tools that use the database operations with fallbacks to mock data
5. **Database-Backed Agent** (`customer_service_db/db_agent.py`): Agent that uses the database-backed tools
6. **Database-Backed Streamlit App** (`streamlit_app_db.py`): Streamlit app that works with the database-backed agent

## Database Schema

The database has the following tables:

- **customers**: Customer information
- **addresses**: Customer addresses
- **communication_preferences**: Customer preferences for email, SMS, etc.
- **sports_profiles**: Customer sports preferences and skill levels
- **products**: Product catalog
- **cart_items**: Items in customer shopping carts
- **orders**: Customer orders
- **order_items**: Items within orders
- **appointments**: Service appointments

## Getting Started

### Prerequisites

- Python 3.11+
- Google ADK (Agent Development Kit)
- SQLAlchemy
- Streamlit

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Test the database implementation:
   ```bash
   python test_db_implementation.py
   ```

3. Run the application locally:
   ```bash
   python start_db_service.py
   ```

   This will:
   - Initialize the database with sample data
   - Test database operations
   - Start the agent
   - Start the Streamlit app on port 8501

### Command-line Options

The `start_db_service.py` script supports several options:

```bash
# Start both agent and Streamlit on the default port (8501)
python start_db_service.py

# Start both agent and Streamlit on a custom port
python start_db_service.py --port 8502

# Start only the agent (useful for debugging)
python start_db_service.py --agent-only

# Start only the Streamlit app (requires agent to be running already)
python start_db_service.py --streamlit-only
```

## Database Operations

Each database operation is implemented with error handling and fallbacks to mock data if the database fails. This ensures the system continues to function even if there are database issues.

### Supported Operations

- **Customer Management**: 
  - Get customer information
  - Update customer preferences
  - Access purchase history

- **Cart Management**:
  - View cart contents
  - Add/remove items from cart
  - Calculate cart totals

- **Product Operations**:
  - Get product recommendations
  - Check product availability
  - Browse product catalog

- **Order Management**:
  - Create orders from carts
  - View order history
  - Update order status

- **Service Scheduling**:
  - Schedule appointments
  - Check available time slots
  - Manage appointment details

## Sample Data

The database is initialized with sample data including:
- Sample customer ("Alex Johnson")
- Various sports products (tennis, running, basketball)
- Sample cart items and order history
- Service appointment options

## Extending the Database

To add new functionality:

1. Update models in `database/models.py`
2. Add operations in `database/operations.py`
3. Add sample data in `database/init_db.py`
4. Update tools in `customer_service_db/db_tools.py`

### Product Images

Product images are stored using Google Cloud Storage (GCS) with the following HTTP URL format:
```
https://storage.cloud.google.com/bettersale-product-images/{sport}/{category}/{product_id}.jpg
```

Images are named using the product ID with hyphens replaced by underscores and converted to lowercase:
- Example: Product ID `TEN-SHOE-001` has image filename `ten_shoe_001.jpg`

To regenerate product data with the correct image URLs:
```bash
python -m customer_service.database.add_products
```

If you need to update existing product images to use the correct HTTP URLs:
```bash
python -m customer_service.database.update_image_urls
```

## Troubleshooting

- **Database Issues**: 
  - Check if the database file exists at `database/bettersale.db`
  - Run `python -m database.init_db` to reinitialize the database

- **Agent Connection Issues**: 
  - Verify the agent is running (`python run_db_agent.py`)
  - Check for error messages in the agent logs

- **Streamlit Issues**:
  - Verify the AGENT_BASE_URL environment variable is set correctly
  - Check the Streamlit logs for connection errors

## Files and Scripts

- `start_db_service.py`: Main script to start the database-backed agent and Streamlit app
- `test_db_implementation.py`: Script to test database functionality
- `run_local.py`: Alternative script to run the application locally
- `database/models.py`: Database schema definitions
- `database/operations.py`: Database operations implementation
- `database/init_db.py`: Database initialization script
- `customer_service_db/db_tools.py`: Database-backed tool implementations
- `customer_service_db/db_agent.py`: Database-backed agent implementation
- `streamlit_app_db.py`: Database-backed Streamlit app