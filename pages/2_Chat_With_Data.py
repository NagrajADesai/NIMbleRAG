import streamlit as st
import nest_asyncio
nest_asyncio.apply()
import time
from src.config import AppConfig, ModelConfig
from src.retrieval_engine import RetrievalEngine
from src.vector_manager import VectorStoreManager
from src.agent_graph import build_graph
from src.voice_handler import transcribe_audio


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
    if "agent_app" not in st.session_state:
        st.session_state.agent_app = None
    if "voice_question" not in st.session_state:
        st.session_state.voice_question = None
    if "last_audio_hash" not in st.session_state:
        st.session_state.last_audio_hash = None


def load_agent(db_name, vector_manager, retrieval_engine):
    """Loads the agent for the selected DB."""
    try:
        db_path = vector_manager.get_db_path(db_name)
        retrieval_engine.initialize_vector_store(text_chunks=None, save_path=db_path)
        retriever = retrieval_engine.get_hybrid_retriever()
        return build_graph(retriever)
    except Exception as e:
        st.error(f"Error loading database '{db_name}': {e}")
        return None


def run_agent(agent_app, user_question):
    """Invoke the agent and return answer, sources, and steps."""
    inputs = {"question": user_question}
    final_state = agent_app.invoke(inputs)
    answer_text = final_state.get("generation", "I couldn't generate an answer.")
    source_docs = final_state.get("documents", [])
    steps = final_state.get("steps", [])
    return answer_text, source_docs, steps


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
                    source = doc.metadata.get('source', 'Unknown')
                    page = doc.metadata.get('page', 'Unknown')
                    st.markdown(f"**{i+1}.** *{source}* (Page {page})")


def display_agent_response(agent_app, user_question):
    """Stream and display the agent response bubble."""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        steps_display = st.status("🧠 Agent Thinking...", expanded=True)

        try:
            answer_text, source_docs, steps = run_agent(agent_app, user_question)

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
                        source = doc.metadata.get('source', 'Unknown')
                        page = doc.metadata.get('page', 'Unknown')
                        content_preview = doc.page_content[:200].replace("\n", " ") + "..."
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

    vector_manager = VectorStoreManager()
    retrieval_engine = RetrievalEngine()
    dbs = vector_manager.list_dbs()

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

        # Native Streamlit audio recorder (no ffmpeg needed)
        audio_input = st.audio_input(
            label="Click to record",
            key="voice_recorder",
        )

        if audio_input is not None:
            audio_bytes = audio_input.read()
            audio_hash = hash(audio_bytes)

            # Only transcribe when a NEW recording is detected
            if audio_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = audio_hash
                st.session_state.voice_question = None  # Reset previous

                with st.spinner("🎙️ Transcribing with Whisper..."):
                    try:
                        transcript = transcribe_audio(audio_bytes)
                        if transcript:
                            st.session_state.voice_question = transcript
                        else:
                            st.warning("Transcript was empty. Please try again.")
                    except Exception as e:
                        st.error(f"Transcription error: {e}")

        # Show transcript + submit controls
        if st.session_state.voice_question:
            st.markdown("---")
            st.markdown("**📝 You said:**")
            # Highlighted box showing what was spoken
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
            with st.spinner(f"Loading Agent for '{selected_db}'..."):
                st.session_state.agent_app = load_agent(
                    selected_db, vector_manager, retrieval_engine
                )

    # ── Chat Area ────────────────────────────────────────────────────────────
    if not st.session_state.agent_app:
        if not dbs:
            st.info("👈 Please create a Knowledgebase first.")
    else:
        # Render chat history
        for msg in st.session_state.messages:
            render_chat_message(msg)

        # ── Handle pending VOICE question ─────────────────────────────────────
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

            display_agent_response(st.session_state.agent_app, pending_voice)

        # ── Typed question via chat input ─────────────────────────────────────
        if user_question := st.chat_input("Ask a question... or use 🎙️ Voice Input →"):
            with st.chat_message("user"):
                st.markdown(user_question)

            st.session_state.messages.append({
                "role": "user",
                "content": user_question,
                "via_voice": False,
            })

            display_agent_response(st.session_state.agent_app, user_question)


if __name__ == "__main__":
    main()
