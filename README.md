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
- Poetry (for dependency management)
- Google ADK SDK (installed via Poetry)
- Google Cloud Project (for Vertex AI Gemini integration)

### Installation
1.  **Prerequisites:**

    For the Agent Engine deployment steps, you will need
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

1.  Clone the repository:

    ```bash
    git clone https://github.com/google/adk-samples.git
    cd agents/customer-service
    ```

    For the rest of this tutorial **ensure you remain in the `agents/customer-service` directory**.

2.  Install dependencies using Poetry:

- if you have not installed poetry before then run `pip install poetry` first. the you can create your virtual environment and install all dependencies using:

  ```bash
  poetry install
  ```

  To activate the virtual environment run:

  ```bash
  poetry env activate
  ```

3.  Set up Google Cloud credentials:

    - Ensure you have a Google Cloud project.
    - Make sure you have the Vertex AI API enabled in your project.
    - Set the `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT`, and `GOOGLE_CLOUD_LOCATION` environment variables. You can set them in your `.env` file (modify and rename .env_sample file to .env) or directly in your shell. Alternatively you can edit [customer_service/config.py](./customer_service/config.py)

    ```bash
    export GOOGLE_CLOUD_PROJECT=YOUR_ROJECT_NAME_HERE
    export GOOGLE_GENAI_USE_VERTEXAI=1
    export GOOGLE_CLOUD_LOCATION=us-central1
    ```

## Running the Agent

You can run the agent using the ADK commant in your terminal.
from the root project directory:

1.  Run agent in CLI:

    ```bash
    adk run customer_service
    ```

2.  Run agent with ADK Web UI:
    ```bash
    adk web
    ```
    Select the customer_service from the dropdown

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

## Evaluating the Agent

Evaluation tests assess the overall performance and capabilities of the agent in a holistic manner.

**Steps:**

1.  **Run Evaluation Tests:**

    ```bash
    pytest eval
    ```

    - This command executes all test files within the `eval` directory.

## Unit Tests

Unit tests focus on testing individual units or components of the code in isolation.

**Steps:**

1.  **Run Unit Tests:**

    ```bash
    pytest tests/unit
    ```

    - This command executes all test files within the `tests/unit` directory.

## Configuration

You can find further configuration parameters in [customer_service/config.py](./customer_service/config.py). This incudes parameters such as agent name, app name and llm model used by the agent.

## Deployment on Google Agent Engine

In order to inherit all dependencies of your agent you can build the wheel file of the agent and run the deployment.

1.  **Build Customer Service Agent WHL file**

    ```bash
    poetry build --format=wheel --output=deployment
    ```

1.  **Deploy the agent to agents engine**
    It is importand to run deploy.py from withing deployment folder so paths are correct

    ```bash
    cd deployment
    python deploy.py
    ```

### Testing deployment

This code snippet is an example of how to test the deployed agent.

```
import vertexai
from customer_service.config import Config
from vertexai.preview.reasoning_engines import AdkApp


configs = Config()

vertexai.init(
    project="<GOOGLE_CLOUD_LOCATION_PROJECT_ID>",
    location="<GOOGLE_CLOUD_LOCATION>"
)

# get the agent based on resource id
agent_engine = vertexai.agent_engines.get('DEPLOYMENT_RESOURSE_NAME') # looks like this projects/PROJECT_ID/locations/LOCATION/reasoningEngines/REASONING_ENGINE_ID

for event in remote_agent.stream_query(
    user_id=USER_ID,
    session_id=session["id"],
    message="Hello!",
):
    print(event)

```
