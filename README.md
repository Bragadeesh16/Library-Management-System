# Project Name: LMS (Library Management System)

## 1. How to Run the Project

### Prerequisites
Ensure the following are installed on your system:

- Python 3.10+
- Flask
- SQLAlchemy
- SQLite (or any other database of your choice)

### Installation Steps
1. **Clone the repository**:

    ```bash
    git clone https://github.com/Bragadeesh16/Library-Management-System.git
    cd LMS
    ```

2. **Set up a virtual environment**:

    ```bash
    python3 -m venv env
    source env/bin/activate  # For Linux/MacOS
    env\Scripts\activate     # For Windows
    ```

3. **Install the required dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Flask app**:

    ```bash
    flask --app app run
    ```

   The application will be accessible at [http://127.0.0.1:5000](http://127.0.0.1:5000).

### Running the Project in Development Mode
Ensure `debug=True` in your `app.py` to enable live reloading and debugging.

