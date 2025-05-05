# Getting Started with the Database-Backed Implementation

This guide will help you set up and run the database-backed version of the BetterSale Sports customer service agent.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the test script to verify database functionality:**
   ```bash
   python test_db_implementation.py
   ```

3. **Start the agent and Streamlit app:**
   ```bash
   python start_db_service.py
   ```

4. **Open the Streamlit app in your browser:**
   [http://localhost:8501](http://localhost:8501)

## Database Structure

The database includes:
- **customers**: User information and preferences
- **products**: Sports equipment catalog
- **cart_items**: Items in customer shopping carts
- **orders & order_items**: Customer order history
- **appointments**: Service appointments like tennis lessons

The database is stored at `database/bettersale.db`.

## Command-line Options

The `start_db_service.py` script has several useful options:

```bash
# Start agent and Streamlit on non-default ports
python start_db_service.py --port 8502 --agent-port 8081

# Start only the agent (helpful for debugging)
python start_db_service.py --agent-only

# Start only the Streamlit app (requires agent already running)
python start_db_service.py --streamlit-only
```

## Database Sample Data

The default customer is **Alex Johnson** with ID `123`. The database is initialized with:
- Products for tennis, running, and basketball
- Sample cart with running shoes and socks
- Sample order history
- Customer sports preferences

## Testing Agent Tools

The agent includes several database-backed tools:
- `access_cart_information`: Get the current cart contents
- `modify_cart`: Add or remove items from the cart
- `get_product_recommendations`: Get product suggestions by sport
- `schedule_service`: Book appointments like tennis lessons
- `update_salesforce_crm`: Process orders

## Troubleshooting

- **Database errors**: Ensure SQLAlchemy is installed. Try reinitializing with `python -m database.init_db`
- **Agent connection issues**: Check that the agent is running on the correct port
- **Streamlit errors**: Verify the `AGENT_BASE_URL` environment variable is set correctly

For more details, see the [README_DB.md](README_DB.md) file.