use axum::{
    extract::Query,
    response::Html,
    routing::get,
    http::StatusCode,
    Json, Router, Extension
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use sqlx::mysql::{MySqlPoolOptions, MySqlPool};
use tera::Tera;
use tera::Context;

#[tokio::main]
async fn main() {

    let tera: Tera = match Tera::new("templates/**/*") {
        Ok(t) => t,
        Err(e) => {
            println!("Parsing error(s): {}", e);
            ::std::process::exit(1);
        }
    };

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
        .route("/barcode/lookup", get(barcode_lookup))
        .route("/barcode/template", get(barcode_template))
        .layer(Extension(pool))
        .layer(Extension(tera));

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

async fn get_barcode(barcode: String, pool: MySqlPool) -> Option<BarcodeModel>{
    return sqlx::query_as!(
        BarcodeModel,
        r#"
        select 
        barcode_id      `id: u64`, 
        barcode         `code: String`,
        status          `status: BarcodeType`
        from barcodes where barcode = ?"#,
        barcode
    )
    .fetch_optional(&pool).await.unwrap();
}

async fn barcode_lookup(
    Query(payload): Query<BarcodeInput>, Extension(pool): Extension<MySqlPool>, 
) -> (StatusCode, Result<Json<BarcodeModel>, String>) {
    return match get_barcode(payload.barcode, pool).await {
        Some(item) => (StatusCode::OK, Ok(Json(item))),
        None => (StatusCode::NOT_FOUND, Err(String::from("Not Found")))
    }
}

async fn barcode_template(
    Query(payload): Query<BarcodeInput>, Extension(pool): Extension<MySqlPool>, Extension(engine): Extension<Tera>,
) -> (StatusCode, Result<Html<String>, Html<String>>) {

    let barcode : Option<BarcodeModel> = get_barcode(payload.barcode, pool).await;

    let mut context = Context::new();

    if let Some(item) = barcode {
        context.insert("barcode", &item);
        return match engine.render("barcode.html", &context) {
            Ok(output) => (StatusCode::OK, Ok(Html(output))),
            Err(err) => (StatusCode::INTERNAL_SERVER_ERROR, Err(Html(err.to_string())))
        }
    } else {
        context.insert("err", "no such barcode");
        return match engine.render("not-found.html", &context) {
            Ok(output) => (StatusCode::NOT_FOUND, Ok(Html(output))),
            Err(err) => (StatusCode::INTERNAL_SERVER_ERROR, Err(Html(err.to_string())))
        }
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

#[derive(Serialize)]
pub struct PageModel {
    barcode: Option<BarcodeModel>
}

#[derive(Serialize)]
pub struct ErrPageModel {
    err: &'static str
}


