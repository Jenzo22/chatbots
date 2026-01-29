"""Convenience entrypoint: python main.py."""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("enterprise_invoice_agent.app:app", host="0.0.0.0", port=8000)
