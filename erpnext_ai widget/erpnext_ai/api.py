import frappe
from frappe.utils import now_datetime
from erpnext_ai.settings import get_settings
from erpnext_ai.rag_client import rag_health, rag_chat

@frappe.whitelist(methods=["POST"])
def chat(message: str):
    """
    Widget entrypoint.
    1. Widget (JS) calls this method.
    2. This method calls FastAPI Agent.
    3. Returns the answer back to Widget.
    """
    try:
        # Call the Agent
        out = rag_chat(message=message, timeout=120)
        
        # FastAPI returns {"response": "..."}
        # We handle fallback keys just in case
        answer_text = out.get("response") or out.get("answer") or str(out)

    except Exception as e:
        frappe.log_error(f"AI Agent Error: {str(e)}")
        return {
            "reply": f"Error connecting to AI Agent: {str(e)}",
            "raw": str(e)
        }

    return {
        "reply": answer_text,
        "raw": out,
        "meta": {
            "site": frappe.local.site,
            "user": frappe.session.user,
            "ts": now_datetime().isoformat(),
        },
    }

@frappe.whitelist(methods=["GET"])
def get_ai_settings():
    s = get_settings()
    return {
        "enabled": s.enabled,
        "ollama_url": s.ollama_url,
        "model": s.model,
        "timeout_seconds": s.timeout_seconds,
    }

@frappe.whitelist(methods=["GET"])
def ai_health():
    return rag_health(timeout=5)