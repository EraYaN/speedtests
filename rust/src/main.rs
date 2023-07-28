use axum::{
    routing::get,
    http::StatusCode,
    Json, Router, extract::Query, Extension
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use sqlx::mysql::{MySqlPoolOptions, MySqlPool};

#[tokio::main]
async fn main() {
    // initialize tracing
    tracing_subscriber::fmt::init();

    let connection_string = std::env::var("DATABASE_URL")
    .unwrap_or("mysql://root:testpassword@percona:33306/speedtest".to_string());

    let pool = MySqlPoolOptions::new()
        .max_connections(100)
        .min_connections(2)
        .connect_lazy(&connection_string).unwrap();

    // build our application with a route
    let app = Router::new()
        .route("/", get(root))
        .route("/barcode/lookup", get(barcode_scan))
        .layer(Extension(pool));

    // run our app with hyper
    // `axum::Server` is a re-export of `hyper::Server`
    let addr = SocketAddr::from(([0, 0, 0, 0], 3000));
    tracing::info!("listening on {}", addr);
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}

async fn root() -> (StatusCode, &'static str) {
    return (StatusCode::OK, "This is an API server, please use the correct client.")
}

async fn barcode_scan(
    Query(payload): Query<BarcodeInput>, Extension(pool): Extension<MySqlPool>, 
) -> (StatusCode, Result<Json<BarcodeModel>, String>) {

    let barcode : Option<BarcodeModel> = sqlx::query_as!(
        BarcodeModel,
        r#"
        select 
        barcode_id      `id: u64`, 
        barcode         `code: String`,
        status          `status: BarcodeType`
        from barcodes where barcode = ?"#,
        payload.barcode
    )
    .fetch_optional(&pool).await.unwrap();

    return match barcode {
        Some(item) => (StatusCode::OK, Ok(Json(item))),
        None => (StatusCode::NOT_FOUND, Err(String::from("Not Found")))
    }

    
}

#[derive(Deserialize)]
struct BarcodeInput {
    barcode: String,
}

#[derive(Debug, Serialize, Clone, Deserialize, sqlx::Type)]
#[sqlx(rename_all = "snake_case")]
#[serde(rename_all = "snake_case")]
enum BarcodeType
{
    Created,
    Downloaded,
    Used,
    Returned,
    Expired
}

#[derive(Debug, Deserialize, Serialize, sqlx::FromRow)]
#[allow(non_snake_case)]
struct BarcodeModel {
    id: u64,
    code: String,
    status: BarcodeType,
}
