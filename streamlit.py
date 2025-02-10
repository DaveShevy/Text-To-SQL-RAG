import streamlit as st
import logging
from main import initialize_backend, process_user_query
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set base directory
base_dir = os.path.dirname(os.path.abspath(__file__))


def main():
    # Set Streamlit Page
    st.set_page_config(page_title='AI Assistant', page_icon="🤖", layout="wide")

    # Set columns
    col1, col2 = st.columns([1, 5])  # The middle column is wider to better center the text

    with col2:
        st.title('Virtual Assistant')

    # Start Logging
    logger.info("Starting Streamlit UI with function-calling + memory approach.")

    # Init backend
    try:
        state = initialize_backend()
    except Exception as e:
        st.error(f"Backend Initialization Error: {e}")
        return

    # Setup chat history if not present

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "user_input" not in st.session_state:
        st.session_state.user_input = ""


    # Function to handle submission
    def submit():
        st.session_state.user_input = st.session_state.widget
        st.session_state.widget = ""  # Clear the widget input

    # User input with widget key
    st.text_input("Ask me something about your survey results:", key="widget", on_change=submit)

    # 4) Process input when the user presses Enter or clicks Submit
    if st.session_state.user_input:
        try:
            user_msg_inp = st.session_state.user_input.strip()

            # Append the user's message to the chat history
            st.session_state.chat_history.append(
                {"role": "user", "content": user_msg_inp}
            )

            # Now process the conversation
            updated_conv = process_user_query(st.session_state.chat_history, state)

            # Overwrite chat history with updated conversation
            st.session_state.chat_history = updated_conv

            # Reset input field by updating the widget
            st.session_state.user_input = ""

        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Display the chat history in reverse order (latest message first)
    for message in reversed(st.session_state.chat_history):
        if message["role"] == "assistant":
            st.markdown(
                f"""
                <div style="
                    background-color: #dfdfdf;
                    color: #000000;
                    padding: 10px 15px;
                    border-radius: 15px;
                    margin: 10px 0 10px 0;
                    max-width: 60%;
                    text-align: left;
                    align-self: flex-start;
                    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
                    ">
                    <b>Assistant:</b> {message['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif message["role"] == "user":
            st.markdown(
                f"""
                <div style="
                    background-color: #0d6efd;
                    color: #ffffff;
                    padding: 10px 15px;
                    border-radius: 15px;
                    margin: 10px 0;
                    max-width: 60%;
                    text-align: right;
                    align-self: flex-end;
                    float: right;
                    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
                    ">
                    <b>You:</b> {message['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif message["role"] == "function":
            # Skip displaying function calls to the user if desired
            pass
        else:
            # For system or other roles, handle accordingly or ignore
            pass

if __name__ == "__main__":
    main()

