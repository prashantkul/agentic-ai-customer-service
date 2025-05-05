# BetterSale Sports Customer Service Agent

This project implements an AI-powered customer service agent for BetterSale Sports, a retail company specializing in sports equipment, athletic wear, and related supplies. The agent is designed to provide excellent customer service, assist customers with product selection, manage orders, schedule services like training sessions, and offer personalized sports equipment recommendations.

## Overview

The BetterSale Sports Customer Service Agent is designed to provide a seamless and personalized shopping experience for customers. It leverages Gemini to understand customer needs, offer tailored sports equipment recommendations, manage orders, and schedule services like training sessions and lessons. The agent is designed to be friendly, empathetic, and highly efficient, ensuring that customers receive the best possible service.

## Agent Details

The key features of the Customer Service Agent include:

| Feature            | Description             |
| ------------------ | ----------------------- |
| _Interaction Type_ | Conversational          |
| _Complexity_       | Intermediate            |
| _Agent Type_       | Single Agent            |
| _Components_       | Tools, Multimodal, Live |
| _Vertical_         | Retail                  |

### Agent Architecture

![Customer Service Agent Workflow](customer_service_workflow.png)

The agent is built using a multi-modal architecture, combining text and image inputs to provide a rich and interactive experience. Customers can share images of sports equipment, apparel, or their current gear to receive accurate product recommendations. The agent (displaying the distinctive BetterSale logo) mocks interactions with various tools and services, including a sports product catalog, inventory management, order processing, and appointment scheduling systems for sports-related services. It also utilizes a session management system to maintain context across interactions and personalize the customer experience.

It is important to notice that this agent is not integrated to an actual backend and the behavior is based on mocked tools. If you would like to implement this agent with actual backend integration you will need to edit [customer_service/tools.py](./customer_service/tools/tools.py)

Because the tools are mocked you might notice that some requested changes will not be applied. For instance newly added items to cart will not show if later a user asks the agent to list all items.

### Key Features

- **Personalized Customer Assistance:**
  - Greets returning customers by name and acknowledges their purchase history.
  - Maintains a friendly, empathetic, and helpful tone.
- **Product Identification and Recommendation:**
  - Assists customers in identifying sports equipment needs based on their activities.
  - Analyzes customer-shared images of equipment, apparel, or playing environments.
  - Provides tailored product recommendations based on visual assessment, identified sports interests, customer skill level, and preferences.
  - Offers alternatives to items in the customer's cart if better options exist.
  - Shows product images with the BetterSale logo for brand consistency.
- **Order Management:**
  - Accesses and displays the contents of a customer's shopping cart.
  - Modifies the cart by adding and removing items based on recommendations and customer approval.
  - Informs customers about relevant sales and promotions on sports equipment.
- **Upselling and Service Promotion:**
  - Suggests relevant services, such as training sessions and lessons.
  - Handles inquiries about pricing and discounts, including competitor offers.
  - Requests manager approval for discounts when necessary.
- **Appointment Scheduling:**
  - Schedules appointments for training sessions, lessons, and equipment fittings.
  - Checks available time slots and presents them to the customer.
  - Confirms appointment details and sends a confirmation/calendar invite.
- **Customer Support and Engagement:**
  - Sends via SMS or email training tips relevant to the customer's sports interests.
  - Provides product images with the BetterSale logo for visual guidance.
  - Offers a discount QR code featuring the BetterSale logo for future in-store purchases to loyal customers.
  - Analyzes customer-shared images of products for troubleshooting or warranty issues.
- **Tool-Based Interactions:**
  - The agent interacts with the user using a set of tools.
  - The agent can use multiple tools in a single interaction.
  - The agent can use the tools to get information and to modify the user's transaction state.
- **Evaluation:**
  - The agent can be evaluated using a set of test cases.
  - The evaluation is based on the agent's ability to use the tools and to respond to the user's requests.

#### Agent State - Default customer information

The agent's session state is preloaded with sample customer data, simulating a real conversation. Ideally, this state should be loaded from a CRM system at the start of the conversation, using the user's information. This assumes that either the agent authenticates the user or the user is already logged in. If this behavior is expected to be modified edit the [get_customer(current_customer_id: str) in customer.py](./customer_service/entities/customer.py)

#### Tools

The agent has access to the following tools:

- `analyze_product_image(image_url: str) -> dict`: Analyzes customer-provided images of sports equipment to identify products and provide recommendations.
- `approve_discount(type: str, value: float, reason: str) -> str`: Approves a discount (within pre-defined limits).
- `sync_ask_for_approval(type: str, value: float, reason: str) -> str`: Requests discount approval from a manager.
- `update_salesforce_crm(customer_id: str, details: str) -> dict`: Updates customer records in Salesforce.
- `access_cart_information(customer_id: str) -> dict`: Retrieves the customer's cart contents.
- `modify_cart(customer_id: str, items_to_add: list, items_to_remove: list) -> dict`: Updates the customer's cart.
- `get_product_recommendations(sport_or_activity: str, customer_id: str) -> dict`: Suggests suitable sports products.
- `check_product_availability(product_id: str, store_id: str) -> dict`: Checks product stock.
- `schedule_service(customer_id: str, service_type: str, date: str, time_range: str, details: str) -> dict`: Books a service appointment (e.g., 'Tennis Lesson', 'Bike Tune-up').
- `get_available_service_times(service_type: str, date: str) -> list`: Retrieves available time slots for a specific service.
- `send_training_tips(customer_id: str, sport: str, delivery_method: str) -> dict`: Sends training tips for a specific sport.
- `generate_qr_code(customer_id: str, discount_value: float, discount_type: str, expiration_days: int) -> dict`: Creates a BetterSale-branded discount QR code.
- `get_product_images(product_id: str) -> list`: Retrieves BetterSale product images with logo for display to the customer.

## Setup and Installations

### Prerequisites

- Python 3.11+
- Conda (for environment management)
- Docker (optional, for containerization)
- Google Cloud Project (optional, for Vertex AI Gemini integration and deployment)

### Installation
1.  **Prerequisites:**

    For the Google Cloud deployment steps, you will need
    a Google Cloud Project. Once you have created your project,
    [install the Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
    Then run the following command to authenticate with your project:
    ```bash
    gcloud auth login
    ```
    You also need to enable certain APIs. Run the following command to enable
    the required APIs:
    ```bash
    gcloud services enable aiplatform.googleapis.com
    ```

2.  Clone the repository:

    ```bash
    git clone https://github.com/prashantkul/agentic-ai-customer-service.git
    cd agentic-ai-customer-service
    ```

3.  Create a new conda environment and install dependencies:

    ```bash
    # Create a new conda environment with Python 3.11
    conda create -n bettersale python=3.11
    conda activate bettersale
    
    # Install uv for faster package installation
    pip install uv
    
    # Use uv to install packages from requirements.txt
    uv pip install -r requirements.txt
    ```

4.  Set up Google Cloud credentials:

    - Copy the `.env.example` file to `.env`:
      ```bash
      cp .env.example .env
      ```
    
    - Edit the `.env` file with your Google Cloud credentials:
      ```
      # Choose 1 for Gemini Vertex AI or 0 Gemini Developer API 
      GOOGLE_GENAI_USE_VERTEXAI=1
      
      # Vertex backend config
      GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID_HERE
      GOOGLE_CLOUD_LOCATION=us-central1
      ```
      
    - If you're using the Gemini Developer API instead of Vertex AI, set:
      ```
      GOOGLE_GENAI_USE_VERTEXAI=0
      GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE
      ```

## Running the Application

You can run the application in several ways:

1. **Run the Streamlit web application locally:**

   ```bash
   streamlit run shopping_agent.py
   ```

2. **Run the database-enabled Streamlit application:**

   ```bash
   cd local_tests
   python streamlit_app_db.py
   ```

3. **Run with Docker:**

   ```bash
   docker build -t bettersale-app .
   docker run -p 8501:8501 bettersale-app
   ```

   Then visit `http://localhost:8501` in your browser.

### Example Interaction

Here's a quick example of how a user might interact with the agent:

**User:**:
hi there

**Agent**:
Hey Alex, I see you've been a BetterSale Sports customer for a couple of years now - we appreciate your business! I also see you have a few things in your cart already. How can I help you find the right sports equipment today?

**User**:
Yeah, I'm looking for some new tennis equipment. I'm not sure which racket would be best for me as an intermediate player. I also need to get some tennis balls and maybe new shoes.

**Agent**:
I'd be happy to help you find the right tennis equipment for your intermediate level! I see from your profile that you've purchased tennis gear before. To best help you with racket selection, could you share a photo of your current racket? That would help me recommend the most suitable upgrade.

**User**:
Sure, here's a photo of my current racket. [shares image]

**Agent**:
Thanks for sharing that image, Alex! I can see you're currently using a Wilson Clash 100 racket, which is a good choice for beginners to intermediate players. Based on your progression to intermediate level, I'd recommend the BetterSale Pro Series 300 racket, which offers more control and power for your developing technique.

I've also noticed the grip seems a bit worn. Would you like me to add grip tape to your recommendations as well?

**User**:
Yes, please add grip tape and also recommend some good tennis balls.

**Agent**:
Great! I've found some excellent options for you from our BetterSale collection:

1. BetterSale Pro Series 300 Tennis Racket - $189.99
2. BetterSale Premium Grip Tape (3-pack) - $12.99
3. BetterSale Tournament-Grade Tennis Balls (can of 4) - $8.99

Would you like me to add any of these to your cart?
...


## Deploying on Google Cloud

### Deploying the Streamlit App

To deploy the Streamlit application to Google Cloud Run, follow these steps:

1. **Make sure Docker is installed on your system.**

2. **Run the deployment script which builds and deploys to Cloud Run:**

    ```bash
    ./deploy_to_cloud_run.sh
    ```

    This script will:
    - Build the Docker image
    - Push it to Google Container Registry
    - Deploy the application to Cloud Run
    - Set up necessary permissions

3. **Access your deployed application**

    After deployment completes, you will get a URL where your application is hosted. The application will be publicly accessible at this URL.

### Deploying the Agent

To deploy the agent to Google Cloud Run, use the ADK deploy command:

```bash
# Set your environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export SERVICE_NAME=bettersale-agent
export APP_NAME=bettersale
export AGENT_PATH=customer_service

# Deploy the agent
adk deploy cloud_run --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION --service_name=$SERVICE_NAME --app_name=$APP_NAME --with_ui $AGENT_PATH
```

This will deploy the agent with a web UI interface to Cloud Run.

### Database Deployment (Optional)

If you want to deploy the database separately:

```bash
cd deployment
python deploy_db.py
```

This will create a Cloud SQL PostgreSQL instance and initialize it with the necessary schema.

### Testing the Deployment

You can test your deployed application by visiting the Cloud Run URL provided after deployment completes. The web interface should load and allow you to interact with the shopping assistant.
