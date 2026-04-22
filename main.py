from fastapi import FastAPI
from pydantic import BaseModel
import warnings
import json
from claude_agent_sdk import query, ClaudeAgentOptions

warnings.filterwarnings("ignore")

app = FastAPI()

# هاد الكلاس كيحدد الداتا لي غاتجيه من n8n
class Payload(BaseModel):
    domains: str
    price: str = "$499"
    sent_emails: str = "[]"

SYSTEM_PROMPT = """
Identity: Elite Domain Broker Agent.
Mission: Find buyers and negotiate deals for premium domains.
Rules: 
- ALWAYS output strictly valid JSON array of objects. No markdown tags.
- Keep emails professional and concise.
"""

async def get_leads(domains, sent_emails, price):
    prompt = f"""
    I have these domains available for sale: {domains}
    EXCLUDED EMAILS: {sent_emails}
    Price: {price}
    
    Task:
    1. Pick ONE domain RANDOMLY.
    2. Use WebSearch to find 10 NEW potential business buyers for that domain.
    3. Write a personalized outreach email for each.
    
    Output exactly a JSON array of objects with these keys:
    "domain", "price", "company", "contact_name", "contact_email", "email_subject", "email_body"
    """
    
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            allowed_tools=["WebSearch"],
            system_prompt=SYSTEM_PROMPT
        )
    ):
        if hasattr(message, "result") and message.result:
            return message.result
    return "[]"

@app.post("/prospect")
async def prospect(payload: Payload):
    # ملي n8n يصيفط الطلب، هاد الفانكشن غاتخدم
    result = await get_leads(payload.domains, payload.sent_emails, payload.price)
    
    # باش نضمنو ديما يرجع JSON نقي لـ n8n
    try:
        clean_result = json.loads(result)
        return clean_result
    except:
        return {"raw_result": result}

@app.get("/")
def read_root():
    return {"status": "Agent is running on Render!"}