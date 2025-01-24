use actix_web::{web, App, HttpServer, Responder};
use chrono::{NaiveDateTime, Utc};
use dotenv::dotenv;
use serde::Serialize;
use std::env;
use std::time::SystemTime;
use tokio_postgres::NoTls;
use tokio_postgres::Config;
use deadpool_postgres::{Manager, ManagerConfig, Pool};


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


async fn fetch_signals(pool: web::Data<Pool>,
                        signal_type: web::Path<String>
) -> impl Responder {

    let client = match pool.get().await {
        Ok(conn) => conn,
        Err(e) => {
            eprintln!("Failed to get database connection: {}", e);
            return web::Json(Vec::<Signal>::new());
        }
    };

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
    println!("Fetched data");

    web::Json(signals)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok(); // Load environment variables from .env file

    let mut cfg = Config::new();
    cfg.host(&env::var("DB_HOST").unwrap_or_else(|_| "localhost".to_string()));
    cfg.user(&env::var("DB_USER").unwrap_or_else(|_| "postgres".to_string()));
    cfg.password(&env::var("DB_PASSWORD").unwrap_or_else(|_| "".to_string()));
    cfg.dbname(&env::var("DB_NAME").unwrap_or_else(|_| "machine_data".to_string()));

    // Create the connection pool
    let mgr_config = ManagerConfig { recycling_method: deadpool_postgres::RecyclingMethod::Fast };
    let mgr = Manager::from_config(cfg, NoTls, mgr_config);
    let pool = Pool::builder(mgr).max_size(16).build().unwrap();


    let host = env::var("SERVER_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
    let port: u16 = env::var("SERVER_PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("Invalid port number");

    println!("Starting server on {}:{}", host, port);

    let server = HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(pool.clone()))
            .route("/health",web::get().to(health_check))
            .route("/signals/{signal_type}",web::get().to(fetch_signals))

    })
    .bind((host.as_str(), port))?
    .run();

    // Graceful shutdown: Listen for Ctrl+C or termination signals
    tokio::select! {
        _ = server => {}, // If the server exits for any reason
        _ = tokio::signal::ctrl_c() => {
            println!("Shutting down server gracefully ...");
        },
    }

    Ok(())
}
