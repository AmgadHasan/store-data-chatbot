# Build the docker image
echo "Building the docker image"
docker build . -t bookstore-chatbot:latest
# Scrape and prepare the data from the website
FILE_PATH=$(pwd)/data/books_data.db
if [ -f "$FILE_PATH" ]; then
    echo "File exists. No need to scrape the data"
else
    echo "File does not exist. Running the Docker container to scrape the data..."
    docker run --user root -v $(pwd)/data:/app/data bookstore-chatbot:latest uv run python -m src.scrape
fi
# Run the gradio chatbot
echo "Starting gradio app from container"
docker run -v $(pwd)/data:/app/data -p 7860:7860 --env-file .env bookstore-chatbot:latest