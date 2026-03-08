"""Constants used across the Jaded Rose Core application."""

# ---------------------------------------------------------------------------
# Agent names
# ---------------------------------------------------------------------------
CHATBOT_AGENT: str = "chatbot_agent"
DATA_AGENT: str = "data_agent"
INTELLIGENCE_AGENT: str = "intelligence_agent"
OUTREACH_AGENT: str = "outreach_agent"

# ---------------------------------------------------------------------------
# Pinecone namespaces
# ---------------------------------------------------------------------------
NS_PRODUCTS: str = "products"
NS_FAQS: str = "faqs"
NS_TRENDS: str = "trends"
NS_COMPETITORS: str = "competitors"

# ---------------------------------------------------------------------------
# Chat intent constants (used by the agent router)
# ---------------------------------------------------------------------------
ORDER_TRACKING: str = "order_tracking"
FAQ: str = "faq"
PRODUCT_QUERY: str = "product_query"
RETURNS: str = "returns"
ESCALATE: str = "escalate"

# ---------------------------------------------------------------------------
# Platform constants
# ---------------------------------------------------------------------------
PLATFORM_SHOPIFY: str = "shopify"
PLATFORM_MIRAKL: str = "mirakl"
PLATFORM_REFINED: str = "refined"
