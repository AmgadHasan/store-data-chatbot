import gradio as gr

from src.llm import process_user_question
from src.utils import create_logger

logger = create_logger(logger_name="app")

logger.info("Creating gradio interface")
app = gr.Interface(
    fn=process_user_question,
    inputs="text",
    outputs="text",
    title="Bookstore Chatbot",
    description="A simple chatbot interface. Ask me anything about the books!",
)

# Launch the app
logger.info("Starting gradio app!")
app.launch()
