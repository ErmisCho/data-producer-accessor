use actix_web::{web, App, HttpServer, Responder};
use chrono::{NaiveDateTime, Utc};
use dotenv::dotenv;
use serde::Serialize;
use std::env;
use std::time::SystemTime;
use tokio_postgres::NoTls;

#[derive(Serialize)]
struct HealthStatus {
    status: String,
}

async fn health_check() -> impl Responder {
    web::Json(HealthStatus {
        status: "Service is up and running".to_string(),
    })
}


#[derive(Serialize)]
struct Signal {
    id: i32,
    signal_type: String,
    value: f64,
    timestamp: NaiveDateTime,
}


async fn fetch_signals(signal_type: web::Path<String>) -> impl Responder {
    dotenv().ok(); // Load environment variables from .env file

    // Build the connection string using environment variables
    let host = env::var("DB_HOST").unwrap_or_else(|_| "localhost".to_string());
    let user = env::var("DB_USER").unwrap_or_else(|_| "postgres".to_string());
    let password = env::var("DB_PASSWORD").unwrap_or_else(|_| "".to_string());
    let dbname = env::var("DB_NAME").unwrap_or_else(|_| "machine_data".to_string());

    let connection_string = format!(
        "host={} user={} password={} dbname={}",
        host, user, password, dbname
    );
    println!("Fetching data from to database {} as {}", dbname, user);

    let (client, connection) = match tokio_postgres::connect(&connection_string, NoTls).await {
        Ok(conn) => conn,
        Err(e) => {
            eprintln!("Failed to connect to database: {}", e);
            return web::Json(Vec::<Signal>::new());
        }
    };

    // Spawn a new thread to handle the connection
    tokio::spawn(async move {
        if let Err(e) = connection.await {
            eprintln!("Connection error: {}", e);
        }
    });

    let query = "SELECT id, signal_type, value, timestamp FROM machine_signals \
                 WHERE signal_type = $1 \
                 ORDER BY timestamp DESC LIMIT 10;";

    let rows = match client.query(query, &[&signal_type.as_str()]).await {
        Ok(rows) => rows,
        Err(e) => {
            eprintln!("Query execution error: {}", e);
            return web::Json(Vec::<Signal>::new());
        }
    };

    let signals: Vec<Signal> = rows
        .into_iter()
        .map(|row| {
            let timestamp: SystemTime = row.get(3);
            let datetime = chrono::DateTime::<Utc>::from(timestamp).naive_utc();
            Signal {
                id: row.get(0),
                signal_type: row.get(1),
                value: row.get(2),
                timestamp: datetime,
            }
        })
        .collect();

    web::Json(signals)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok(); // Load environment variables from .env file

    let host = env::var("SERVER_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
    let port: u16 = env::var("SERVER_PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("Invalid port number");

    println!("Starting server on {}:{}", host, port);

    HttpServer::new(|| {
        App::new()
            .route("/health",web::get().to(health_check))
            .route("/signals/{signal_type}",web::get().to(fetch_signals))

    })
    .bind((host.as_str(), port))?
    .run()
    .await
}
