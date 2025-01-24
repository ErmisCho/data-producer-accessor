# Data Producer/Accessor

## 📝 Overview
This project simulates a machine that generates, stores, and retrieves production data. It demonstrates skills in data simulation, database management, and API design using Python and Rust.

## ✨ **Features**
- **Data Generation** (Python):
  - Simulates machine activity, errors, and power consumption.
  - Real-time insertion of generated data into a PostgreSQL database.

- **Data Access** (Rust):
  - RESTful API for querying stored data efficiently.
  - Endpoint: `/signals/{signal_type}` retrieves the last 10 records for a given signal type.

- **Health Monitoring**:
  - A `/health` endpoint to monitor the data accessor service status.

- **Graceful Shutdown**:
  - Handles termination signals (`Ctrl+C`) to ensure clean shutdown and resource release.

## 🚀 **Tech Stack**
- **Backend**:
  - Python (Data Producer)
  - Rust with Actix-Web (Data Accessor)

- **Database**:
  - PostgreSQL (Relational database for storing machine signals)

## 📂 **Project Structure**
```
data-producer-accessor/
├── data_accessor/         # Rust-based accessor service
│   ├── src/
│   │   └── main.rs        # Main Rust code for the accessor service
│   ├── Cargo.toml         # Rust project configuration file
│   └── Cargo.lock         # Dependency lock file for reproducible builds
├── .env.example           # Example environment configuration file
├── .gitignore             # Git ignore file
├── README.md              # Documentation file
├── data_producer.py       # Python-based producer for generating and storing data
├── requirements.txt       # Python dependencies for the producer
└── data_producer.log      # Log example of the Python producer execution
```

## 📑 **API Endpoints**

### **1. Signals API**
Fetch the last 10 records for a specific signal type.

| Endpoint                  | Method | Description                                   |
|---------------------------|--------|-----------------------------------------------|
| `/signals/state_change`   | GET    | Fetch the last 10 state change signals.       |
| `/signals/power`          | GET    | Fetch the last 10 power consumption records.  |
| `/signals/error`          | GET    | Fetch the last 10 error signals.              |

#### **Example Request and Response**

**Request**:
```bash
curl http://127.0.0.1:8080/signals/state_change
```

**Response**:
```json
[
    {
        "id": 1,
        "signal_type": "state_change",
        "value": 1,
        "timestamp": "2025-01-23T10:00:00"
    },
    {
        "id": 2,
        "signal_type": "state_change",
        "value": 0,
        "timestamp": "2025-01-23T10:05:00"
    }
]
```

### **2. Health Check API**
Verify that the service is running and connected to the database.

| Endpoint      | Method | Description                       |
|---------------|--------|-----------------------------------|
| `/health`     | GET    | Returns the service health status.|

#### **Example Request and Response**

**Request**:
```bash
curl http://127.0.0.1:8080/health
```

**Response**:
```json
{
    "status": "Service is up and running"
}
```

---

## ⚙️ **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/ErmisCho/data-producer-accessor.git
cd data-producer-accessor
```

### **2. Setup the Database**
Ensure PostgreSQL is installed and running. Rename `.env.example` to `.env` and populate it with the following variables:

#### `.env` File Example:
```dotenv
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=machine_data
SERVER_HOST=127.0.0.1
SERVER_PORT=8080
```

### **3. Activate Python Virtual Environment**
#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

### **4. Run the Data Producer**
```bash
pip install -r requirements.txt
python producer.py
```

### **5. Run the Data Accessor in a separate terminal**
```bash
cd data_accessor
cargo run
```

---

## 🎯 **Use Cases**
- **IoT Monitoring**: Track machine activities in real-time.
- **Error Analysis**: Investigate operational errors with historical data.
- **Power Optimization**: Analyze and optimize machine power consumption.

## ✅ **Key Highlights**
- **Professional Practices**:
  - Separation of concerns between data production and data access.
  - Graceful shutdown for resource management.
  - Use of connection pooling for efficiency.

- **Scalability**:
  - Designed for adding new endpoints or scaling the database.

- **Interview Readiness**:
  - Showcases real-world skills in Rust, Python, and database integration.

## 📄 **Future Improvements**
- **Authentication**: Add JWT-based authentication for secure data access.
- **Dockerization**: Use Docker to containerize the app for easy deployment.
- **Caching**: Integrate Redis for faster repeated queries.
- **Testing**: Add unit and integration tests to validate functionality.


