
# Car Detection System

## Overview
This Python application is designed to detect cars in video feeds using OpenCV and store the count in a PostgreSQL database. It uses Haar cascades for object detection.

## Requirements
- Python 3.x
- OpenCV
- PostgreSQL
- psycopg2
- Additional requirements can be found in `requirements.txt`.

## Setup
1. **Install Dependencies**: Run `pip install -r requirements.txt` to install the required Python packages.
2. **Database Setup**: Ensure PostgreSQL is installed and running. Create a database and update the `settings.json` file with your database credentials.
3. **Haar Cascade**: Place the `haarcascade_car.xml` file in the project directory.
4. **Docker (Optional)**: Use the provided Dockerfile for containerization.

## Configuration
Edit the `settings.json` file to set up your configuration. Example configuration:
```json
{
    "cascade_name": "haarcascade_car.xml",
    "db_name": "your_db_name",
    "db_user": "your_db_user",
    "db_pass": "your_db_password",
    "db_host": "localhost",
    "video_link": "path_to_video_file_or_stream"
}
```

## Running the Application
Execute the script using:
```
python application.py
```

## Files Description
- `application.py`: The main entry point of the application.
- `computer_vision.py`: Contains the `CarCount` class for car detection and database operations.
- `controls.py`: Utility script to load configuration settings.
- `requirements.txt`: Lists all Python dependencies.
- `haarcascade_car.xml`: Haar cascade file for car detection.
- `settings.json`: Configuration file for database and other settings.

## Usage
The application will start processing the video feed specified in the configuration file. Detected cars will be displayed in a window, and the count will be stored in the PostgreSQL database.
