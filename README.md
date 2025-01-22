# Data Producer/Accessor

## 📝 Overview
This project simulates a machine that generates, stores, and retrieves production data. It demonstrates skills in data simulation, database management, and API design using Python and Rust.

## ✨ Features
- **Data Generation**:
  - **State Change**: Indicates if the machine is active (generated every 1–5 seconds).
  - **Error Reports**: Logs errors during operation (generated every 10–30 seconds).
  - **Power Consumption**: Tracks power usage in watts (generated every 0.01 seconds).
- **Data Storage**: Data is stored in a relational database (**PostgreSQL**).
- **Data Retrieval**: A Rust-based API fetches and processes stored data.

## 🔧 Components
1. **Database**: A PostgreSQL database to store machine data.
2. **Producer**: A Python script simulates and inserts machine data.
3. **Accessor Service**: A Rust-based API provides efficient data retrieval.

## 🚀 Setup
### Prerequisites
- Install **PostgreSQL**.
- Install **Python** (3.7+).
- Install **Rust**.

## ✅ TODO
- Producer: Create a PostgreSQL database if it does not exist
- Producer: Implement a Python script to generate data and insert it into the database.
- Producer: Simulate three data types: state change, error reports, and power consumption.
- Accessor: Implement a RESTful API in Rust to retrieve data based on parameters like signal type or date range.
- Accessor: Define specific API endpoints (e.g., GET `/signals/{type}`).
- Future ToDos: Accessor: Add authentication and caching to the API.
- Future ToDos: Include tests for both the producer and accessor components.

## 🛠 Technologies
- **PostgreSQL**: For data storage.
- **Python**: For data generation.
- **Rust**: For the accessor service.

## 📈 Use Cases
- **IoT Applications**: Monitor real-time machine data.
- **Error Tracking**: Identify operational issues from error logs.
- **Power Optimization**: Analyze and optimize machine power usage.

---
This project highlights practical applications in data simulation, integration, and system design. It is suitable for IoT and analytics scenarios.

