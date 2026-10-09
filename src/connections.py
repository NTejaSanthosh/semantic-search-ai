import os

import ollama
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def get_setting(name):
    value = st.secrets.get(name) if name in st.secrets else None
    return value or os.getenv(name, "")


def get_supabase_client() -> Client:
    url = get_setting("SUPABASE_URL")
    key = get_setting("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Configure SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY in .env or Streamlit secrets."
        )

    return create_client(url, key)


def get_ollama_client() -> ollama.Client:
    host = get_setting("OLLAMA_HOST") or "http://localhost:11434"
    return ollama.Client(host=host)


def test_connections():
    results = {}

    try:
        client = get_supabase_client()
        client.table("app_users").select("id").limit(1).execute()
        results["Supabase"] = "Connected"
    except Exception as exc:
        results["Supabase"] = f"Connection failed: {exc}"

    try:
        client = get_ollama_client()
        response = client.embeddings(
            model=get_setting("OLLAMA_EMBED_MODEL")
            or "nomic-embed-text:latest",
            prompt="Connection test"
        )
        vector = response.get("embedding", [])

        if not vector:
            raise RuntimeError("Ollama returned an empty embedding.")

        results["Ollama embeddings"] = (
            f"Connected; vector dimension: {len(vector)}"
        )
    except Exception as exc:
        results["Ollama embeddings"] = f"Connection failed: {exc}"

    return results