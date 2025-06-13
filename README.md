# TestudoScraper

The TestudoScraper is a Python application designed to help University of Maryland students track course seat availability on Testudo. It periodically scrapes the Testudo course search page and sends email notifications when seats become available for preferred courses and instructors. This project includes a web frontend for easy course tracking management and is containerized for cloud deployment.

## Features

*   **Course Availability Tracking**: Monitors specific courses and sections for open seats.
*   **Email Notifications**: Sends real-time email alerts when desired course seats become available.
*   **User-Friendly Web Frontend**: A Flask-based web interface for users to easily add and manage courses to track.
*   **MongoDB Integration**: Stores user tracking preferences and course availability data in a MongoDB database.
*   **Containerized Deployment**: Packaged with Docker for easy deployment to cloud platforms like AWS App Runner.
*   **Configurable Scraper**: Adjustable scraping intervals and active time windows via environment variables.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.9+**: The project is built with Python.
*   **Docker**: Required for building and running container images.
*   **AWS CLI (Optional)**: Needed if you plan to deploy to AWS App Runner.
*   **MongoDB Atlas Account**: A cloud-hosted MongoDB database is used for data storage.
*   **Mailtrap Account (or other SMTP service)**: Used for sending email notifications.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yashaggarwal/TestudoScraper.git
    cd TestudoScraper
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory of the project and add the following environment variables:

    ```
    MONGODB_URI="your_mongodb_connection_string"
    NOTIFICATION_EMAIL="your_sender_email@example.com"
    SMTP_HOST="your_smtp_host" # e.g., live.smtp.mailtrap.io
    SMTP_PORT=587 # or your SMTP port
    SMTP_USERNAME="your_smtp_username" # e.g., api for Mailtrap
    SMTP_PASSWORD="your_smtp_password" # e.g., your Mailtrap API key
    MONGODB_DB_NAME="testudo_scraper" # Optional, default is testudo_scraper
    MONGODB_USERS_COLLECTION="users" # Optional, default is users
    MONGODB_COURSES_COLLECTION="courses" # Optional, default is courses
    TIMEZONE="US/Pacific" # Optional, e.g., America/New_York
    SCRAPER_START_TIME="04:35" # Optional, HH:MM format (24-hour)
    SCRAPER_END_TIME="19:35" # Optional, HH:MM format (24-hour)
    SCRAPER_INTERVAL_MINUTES=60 # Optional, interval in minutes
    ```

    *   Replace `your_mongodb_connection_string` with your actual MongoDB Atlas connection string.
    *   Replace `your_sender_email@example.com` with the email address you want notifications to come from.
    *   Fill in your SMTP server details. For Mailtrap, `SMTP_HOST` is typically `live.smtp.mailtrap.io` and `SMTP_USERNAME` is `api`.

### Running Locally

To run the Flask web application locally:

```bash
python src/app.py
```
This will start the Flask development server at `http://127.0.0.1:5000` by default.

To run the scraper manually (for testing purposes, it's usually deployed as part of the Docker container):

```bash
python src/scraper/course_scraper.py
```

## Deployment on AWS App Runner

This project is designed to be easily deployed to AWS App Runner using Docker.

1.  **Create an ECR Repository:**
    First, create a repository in Amazon ECR:
    ```bash
    aws ecr create-repository --repository-name testudo-scraper-repo --region us-east-1
    ```
    Note down the repository URI that is returned.

2.  **Build the Docker Image:**
    Ensure you build the image for the correct platform (Linux/x86\_64 for App Runner):
    ```bash
    docker build --platform linux/amd64 -t testudoscraper-apprunner .
    ```

3.  **Authenticate Docker with Amazon ECR:**
    ```bash
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your_account_id.dkr.ecr.us-east-1.amazonaws.com
    ```
    Replace `your_account_id` with your AWS account ID.

4.  **Tag and Push to ECR:**
    First, tag your Docker image:
    ```bash
    docker tag testudoscraper-apprunner:latest your_account_id.dkr.ecr.us-east-1.amazonaws.com/your_ecr_repository_name:latest
    ```
    Then, push the image to your ECR repository:
    ```bash
    docker push your_account_id.dkr.ecr.us-east-1.amazonaws.com/your_ecr_repository_name:latest
    ```
    Replace `your_ecr_repository_name` with the actual name of your ECR repository (e.g., `testudo-scraper-repo`).

5.  **Create/Update App Runner Service:**
    You can create or update your App Runner service using the AWS CLI or the AWS Console. Ensure your App Runner service is configured to use the ECR image you just pushed.
    When creating the service, configure environment variables in App Runner to match those in your local `.env` file (e.g., `MONGODB_URI`, `NOTIFICATION_EMAIL`, etc.).

    Example CLI command to update (after initial creation):
    ```bash
    aws apprunner update-service --service-arn your_apprunner_service_arn --source-configuration '{"ImageRepository":{"ImageIdentifier":"your_account_id.dkr.ecr.us-east-1.amazonaws.com/your_ecr_repository_name:latest","ImageRepositoryType":"ECR"}}' --region us-east-1
    ```
    Replace `your_apprunner_service_arn` with the ARN of your App Runner service.

### Required Environment Variables

The following environment variables are required for the application to function:

*   `MONGODB_URI`: Connection string for your MongoDB Atlas database.
*   `NOTIFICATION_EMAIL`: The email address used as the sender for notifications.
*   `SMTP_HOST`: The SMTP server host for sending emails.
*   `SMTP_PORT`: The SMTP server port.
*   `SMTP_USERNAME`: The username for SMTP authentication.
*   `SMTP_PASSWORD`: The password/API key for SMTP authentication.

### Optional Environment Variables

The following environment variables are optional and have default values:

*   `MONGODB_DB_NAME`: Name of the MongoDB database. Defaults to `testudo_scraper`.
*   `MONGODB_USERS_COLLECTION`: Name of the MongoDB users collection. Defaults to `users`.
*   `MONGODB_COURSES_COLLECTION`: Name of the MongoDB courses collection. Defaults to `courses`.
*   `TIMEZONE`: Timezone for the scraper's active window (e.g., `US/Eastern`, `Europe/London`). Defaults to `US/Pacific`.
*   `SCRAPER_START_TIME`: Start time for the scraper to be active (24-hour format, HH:MM). Defaults to `04:35`.
*   `SCRAPER_END_TIME`: End time for the scraper to be active (24-hour format, HH:MM). Defaults to `19:35`.
*   `SCRAPER_INTERVAL_MINUTES`: How often the scraper runs in minutes. Defaults to `60`.

## Configuration

The following environment variables can be set to configure the application:

*   `MONGODB_URI`: Connection string for your MongoDB Atlas database.
*   `NOTIFICATION_EMAIL`: The email address used as the sender for notifications.
*   `SMTP_HOST`: The SMTP server host for sending emails.
*   `SMTP_PORT`: The SMTP server port.
*   `SMTP_USERNAME`: The username for SMTP authentication.
*   `SMTP_PASSWORD`: The password/API key for SMTP authentication.
*   `MONGODB_DB_NAME`: (Optional) Name of the MongoDB database. Defaults to `testudo_scraper`.
*   `MONGODB_USERS_COLLECTION`: (Optional) Name of the MongoDB users collection. Defaults to `users`.
*   `MONGODB_COURSES_COLLECTION`: (Optional) Name of the MongoDB courses collection. Defaults to `courses`.
*   `TIMEZONE`: (Optional) Timezone for the scraper's active window (e.g., `US/Eastern`, `Europe/London`). Defaults to `US/Pacific`.
*   `SCRAPER_START_TIME`: (Optional) Start time for the scraper to be active (24-hour format, HH:MM). Defaults to `04:35`.
*   `SCRAPER_END_TIME`: (Optional) End time for the scraper to be active (24-hour format, HH:MM). Defaults to `19:35`.
*   `SCRAPER_INTERVAL_MINUTES`: (Optional) How often the scraper runs in minutes. Defaults to `60`.

## Usage

Once the application is running (locally or on App Runner):

1.  Navigate to the application's home page.
2.  Click on "Track Course" in the navigation bar.
3.  Fill in the form with the course ID, your email address, and optionally the section ID and preferred instructors (comma-separated).
4.  Click "Start Tracking."

The scraper will then periodically check for seat availability and send email notifications if seats open up for your tracked courses.

## Contributing

We welcome contributions to the TestudoScraper project! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Write clear commit messages.
5.  Push your branch (`git push origin feature/your-feature-name`).
6.  Create a pull request to the `main` branch of this repository.

Please ensure your code adheres to good coding practices and includes relevant tests where appropriate.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions, feel free to open an issue in the GitHub repository.

