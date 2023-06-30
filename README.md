# APWallet Backend Server

The APWallet Backend Server is a FastAPI application developed in Python.

## Prerequisites
Before you begin, ensure you have met the following requirements:
* You have a machine with Python 3.8 or above installed.
* You have PIP installed. PIP typically comes with the Python installation.
* You have a PostgreSQL server set up. You will need the PostgreSQL server details for configuration purposes.

## Getting Started
Follow these steps to get the APWallet Backend Server running on your machine:

1. Clone the repository:
    ```
    git clone https://github.com/juz410/APWallet_Backend.git
    ```
2. Navigate to the project directory:
    ```
    cd APWallet_Backend
    ```
3. Install the required Python libraries:
    ```
    pip install -r requirements.txt
    ```
4. Create a `.env` file in the root directory of the project, and fill in your specific configuration data:
    ```
    DATABASE_HOSTNAME=
    DATABASE_PORT=
    DATABASE_PASSWORD=
    DATABASE_USERNAME=
    DATABASE_NAME=
    SECRET_KEY=
    GMAIL_PASSWORD=
    EMAIL_USERNAME=
    EMAIL_PASSWORD=
    EMAIL_FROM=
    EMAIL_SMTP_SERVER=
    EMAIL_SMTP_PORT=
    STRIPE_API_KEY=
    PRIVATE_KEY=
    PUBLIC_KEY=
    ```
    **Note:** The `DATABASE_` prefixed variables should be set according to your PostgreSQL server configuration. The application will use these details to establish a connection to your PostgreSQL server.
5. After setting up your `.env` file, start the server with this command:
    ```
    uvicorn main:app --reload
    ```

Now you should have the APWallet backend server running on your machine.

## License

This project is licensed under the terms of the MIT license. For more information, see [LICENSE](LICENSE) file in this repository.

## Feedback
If you have any feedback or run into issues, please contact us via email or open an issue on this repository.
