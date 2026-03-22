import streamlit as st
import time
from api_client import APIClient

def stream_text(text):
    """Yields text one character at a time for streaming effect."""
    for char in text:
        yield char
        time.sleep(0.005)

def initialize_chat_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_db" not in st.session_state:
        st.session_state.current_db = None
    if "voice_question" not in st.session_state:
        st.session_state.voice_question = None
    if "last_audio_hash" not in st.session_state:
        st.session_state.last_audio_hash = None

def render_chat_message(msg):
    """Render a single message from history."""
    with st.chat_message(msg["role"]):
        if msg["role"] == "user" and msg.get("via_voice"):
            st.caption("🎙️ *Voice input*")
        st.markdown(msg["content"])

        if "steps" in msg and msg["steps"]:
            with st.expander("🧠 Agent Thoughts (History)"):
                for step in msg["steps"]:
                    st.write(f"- {step}")

        if "sources" in msg and msg["sources"]:
            with st.expander("📚 Source Citations"):
                for i, doc in enumerate(msg["sources"]):
                    source = doc.get('source', 'Unknown')
                    page = doc.get('page', 'Unknown')
                    st.markdown(f"**{i+1}.** *{source}* (Page {page})")

def display_agent_response(user_question, selected_db):
    """Stream and display the agent response bubble."""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        steps_display = st.status("🧠 Agent Thinking...", expanded=True)

        try:
            # Call backend API
            result = APIClient.send_query(user_question, selected_db)
            
            answer_text = result.get("answer", "I couldn't generate an answer.")
            source_docs = result.get("sources", [])
            steps = result.get("steps", [])

            for step in steps:
                steps_display.write(f"- {step}")
            steps_display.update(
                label="🧠 Agent Finished Thinking", state="complete", expanded=False
            )

            for char in stream_text(answer_text):
                full_response += char
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            if source_docs:
                with st.expander("📚 View Source Citations"):
                    for i, doc in enumerate(source_docs):
                        source = doc.get('source', 'Unknown')
                        page = doc.get('page', 'Unknown')
                        content_preview = doc.get('content', '') + "..."
                        st.markdown(f"**{i+1}.** *{source}* (Page {page})")
                        st.caption(content_preview)

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sources": source_docs,
                "steps": steps,
            })

        except Exception as e:
            steps_display.update(label="❌ Error", state="error")
            st.error(f"Error generating response: {e}")

def main():
    st.set_page_config("Chat With Data", page_icon="💬", layout="wide")
    st.title("💬 Chat With Agent")

    initialize_chat_state()

    dbs = APIClient.get_databases()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Configuration")

        if not dbs:
            st.warning(
                "No Knowledgebases found. Please create one in the "
                "'Creating Knowledgebase' page."
            )
            selected_db = None
        else:
            selected_db = st.selectbox(
                "Select Knowledgebase",
                options=dbs,
                index=(
                    dbs.index(st.session_state.current_db)
                    if st.session_state.current_db in dbs
                    else 0
                ),
            )

        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.voice_question = None
            st.rerun()

        # ── Voice Input Panel ────────────────────────────────────────────────
        st.divider()
        st.subheader("🎙️ Voice Input")
        st.caption("Record your question — Whisper will transcribe it.")

        audio_input = st.audio_input(
            label="Click to record",
            key="voice_recorder",
        )

        if audio_input is not None:
            audio_bytes = audio_input.read()
            audio_hash = hash(audio_bytes)

            if audio_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = audio_hash
                st.session_state.voice_question = None

                with st.spinner("🎙️ Transcribing with Whisper..."):
                    try:
                        transcript = APIClient.transcribe_audio(audio_bytes)
                        if transcript:
                            st.session_state.voice_question = transcript
                        else:
                            st.warning("Transcript was empty. Please try again.")
                    except Exception as e:
                        st.error(f"Transcription error: {e}")

        if st.session_state.voice_question:
            st.markdown("---")
            st.markdown("**📝 You said:**")
            st.info(f'"{st.session_state.voice_question}"')

            edited_transcript = st.text_area(
                label="Edit if needed before submitting:",
                value=st.session_state.voice_question,
                height=75,
                key="voice_transcript_editor",
            )

            col1, col2 = st.columns(2)
            with col1:
                submit_clicked = st.button(
                    "🚀 Submit", use_container_width=True, type="primary"
                )
            with col2:
                discard_clicked = st.button("🗑️ Discard", use_container_width=True)

            if submit_clicked and edited_transcript.strip():
                st.session_state["_pending_voice"] = edited_transcript.strip()
                st.session_state.voice_question = None
                st.rerun()

            if discard_clicked:
                st.session_state.voice_question = None
                st.rerun()

    # ── Handle DB switch ─────────────────────────────────────────────────────
    if selected_db:
        if selected_db != st.session_state.current_db:
            st.session_state.current_db = selected_db
            st.session_state.messages = []

    # ── Chat Area ────────────────────────────────────────────────────────────
    if not selected_db:
        if not dbs:
            st.info("👈 Please create a Knowledgebase first.")
    else:
        for msg in st.session_state.messages:
            render_chat_message(msg)

        pending_voice = st.session_state.pop("_pending_voice", None)
        if pending_voice:
            with st.chat_message("user"):
                st.caption("🎙️ *Voice input — transcribed by Whisper*")
                st.markdown(pending_voice)

            st.session_state.messages.append({
                "role": "user",
                "content": pending_voice,
                "via_voice": True,
            })

            display_agent_response(pending_voice, selected_db)

        if user_question := st.chat_input("Ask a question... or use 🎙️ Voice Input →"):
            with st.chat_message("user"):
                st.markdown(user_question)

            st.session_state.messages.append({
                "role": "user",
                "content": user_question,
                "via_voice": False,
            })

            display_agent_response(user_question, selected_db)

if __name__ == "__main__":
    main()
