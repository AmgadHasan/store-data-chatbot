import gradio as gr

from src.llm import process_user_question

app = gr.Interface(
    fn=process_user_question,
    inputs="text",
    outputs="text",
    title="Bookstore Chatbot",
    description="A simple chatbot interface. Ask me anything about the books!",
)

# Launch the app
app.launch()
