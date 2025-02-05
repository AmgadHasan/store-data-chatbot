from src import utils

books_dataset_tools = [
    {
        "type": "function",
        "function": {
            "name": "query_books_database",
            "description": "Quries the books database using SQL. Returns `None` if no there are no entries for the provided query. The database has the following table:```sql\nCREATE TABLE IF NOT EXISTS books (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    title TEXT NOT NULL,\n    price REAL NOT NULL,\n    star_rating INTEGER NOT NULL,\n    availability TEXT NOT NULL,\n    description TEXT NOT NULL,\n    category TEXT NOT NULL,\n    quantity INTEGER NOT NULL\n    )\n```",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "The sql query to run against the SQLite database. Must be in the SQLite format.",
                    }
                },
                "required": ["sql_query"],
            },
        },
    },
]

llm_tools_map = {
    "query_books_database": utils.query_books_database,
}
