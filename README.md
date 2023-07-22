# StompZone SQLite

`StompZone-SQLite` is a Python Flask application providing a RESTful interface to a SQLite database. This API enables you to easily manage generic tokens by user ID (eg, Discord).

## Installation

1. Clone the repository.
2. Install dependencies using pip:

```
pip install -r requirements.txt
```

3. Export your API Key as an environment variable:

```
export API_KEY=your_api_key_here
```

4. Run the application:

```
python app.py
```

## Endpoints

- GET `/user/<id>`: Retrieve a user's information and their credits. If a user with the given ID does not exist, the endpoint will create a new user with the ID and default credits of 3.
- PUT `/user/<id>`: Update a user's credits. The request body should be JSON with a `"value"` key representing the change in credits. The server will respond with the updated user data. If a user with the given ID does not exist, the server will respond with a 404 status code.

Each request must include an `Authorization` header with the value of your API key.

## Security

The API uses a key-based authentication system. Only requests that include a valid API key in the `Authorization` header will be processed.

## License

StompZone SQL API is licensed under the MIT License.
