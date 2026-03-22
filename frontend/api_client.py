import requests
import streamlit as st
from typing import List, Dict, Any

API_BASE_URL = "http://localhost:8000/api/v1"

class APIClient:
    """Client for interacting with the FastAPI backend."""

    @staticmethod
    def get_databases() -> List[str]:
        try:
            response = requests.get(f"{API_BASE_URL}/knowledgebase/")
            response.raise_for_status()
            return response.json().get("databases", [])
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")
            return []

    @staticmethod
    def upload_documents(db_name: str, files) -> Dict[str, Any]:
        url = f"{API_BASE_URL}/knowledgebase/upload"
        
        files_data = []
        for file in files:
            files_data.append(
                ("files", (file.name, file.getvalue(), file.type))
            )
        
        data = {"db_name": db_name}
        
        try:
            response = requests.post(url, data=data, files=files_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                err_detail = response.json().get("detail", str(e))
            except:
                err_detail = str(e)
            raise Exception(err_detail)
        except Exception as e:
            raise e

    @staticmethod
    def send_query(query: str, database_name: str) -> Dict[str, Any]:
        url = f"{API_BASE_URL}/chat/query"
        payload = {"query": query, "database_name": database_name}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                err_detail = response.json().get("detail", str(e))
            except:
                err_detail = str(e)
            raise Exception(err_detail)
        except Exception as e:
            raise e

    @staticmethod
    def transcribe_audio(audio_bytes: bytes) -> str:
        url = f"{API_BASE_URL}/voice/transcribe"
        files_data = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        try:
            response = requests.post(url, files=files_data)
            response.raise_for_status()
            return response.json().get("transcript", "")
        except requests.exceptions.HTTPError as e:
            try:
                err_detail = response.json().get("detail", str(e))
            except:
                err_detail = str(e)
            raise Exception(err_detail)
        except Exception as e:
            raise e
