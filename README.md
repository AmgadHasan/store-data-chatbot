---
title: Bookstore Chatbot
emoji: 👁
colorFrom: red
colorTo: indigo
sdk: docker
pinned: false
short_description: A chabot for an online bookstore
---
# Bookstore Chatbot
A chatbot to ask questions about products in an online bookstore.

## Setup
This section explains how to setup and run the project
### 1. Clone the project
```sh
git clone https://github.com/AmgadHasan/store-data-chatbot.git
cd store-data-chatbot
```

### 2. Setup environment variables

You need to setup the following environment variables in a `.env` file
```
# .env
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_API_KEY=<your api key here>
CHAT_MODEL=gemma2-9b-it
```

### 3. Installing the project
#### UV

1. Make sure you have installed [uv](https://docs.astral.sh/uv/getting-started/installation/)

2. Install dependencies
```sh
uv sync
```

3. Scrape the data
```sh
uv run python src/scrape.py
```

4. Start the gradio app
Start the gradio app by running:
```sh
uv run python -m src.app
```
This runs the app on localhost

### Docker

1. Install Docker Engine
Make sure you have installed [docker](https://docs.docker.com/engine/install/)

[Optional] Use the run script
The `run.sh` file combines steps 2-4 into one script. You can run it as follows:
```sh
sudo bash run.sh
```

2. Build the docker image
```sh
docker build . -t bookstore-chatbot:latest
```

3. Scrape the data
The following code runs the container to scrape the data. We mount the local `data` folder to save the output data in a persistent manner:
```sh
docker run --user root -v $(pwd)/data:/app/data bookstore-chatbot:latest uv run python src/scrape.py
```

4. Start the gradio app
```sh
docker run -v $(pwd)/data:/app/data -p 7860:7860 --env-file .env bookstore-chatbot:latest
```