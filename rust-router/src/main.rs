mod router;

use std::convert::Infallible;
use std::net::SocketAddr;
use hyper::service::{make_service_fn, service_fn};
use hyper::{Body, Request, Response, Server};
use serde_json::json;
use tokio::time::sleep;
use std::time::Duration;
use metrics_exporter_prometheus::PrometheusBuilder;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

use crate::router::{Router, json_response};

async fn handle_request(
    router: Router,
    req: Request<Body>,
) -> Result<Response<Body>, Infallible> {
    Ok(router.handle_request(req).await)
}

#[tokio::main]
async fn main() {
    // Initialize logging
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .init();

    // Initialize metrics
    let builder = PrometheusBuilder::new();
    builder.install().expect("failed to install recorder/exporter");

    // Create router instance
    let router = Router::new();
    let router_clone = router.clone();

    // Simple route - baseline performance test
    router.add_route("GET", "/ping", |_req| async move {
        json_response(json!({
            "message": "pong",
            "time": chrono::Utc::now()
        }))
        .await
    });

    // Medium complexity route - simulates typical API endpoint
    router.add_route("GET", "/api/v1/data", |_req| async move {
        // Simulate some processing
        sleep(Duration::from_millis(10)).await;

        json_response(json!({
            "id": 123,
            "timestamp": chrono::Utc::now(),
            "data": "Sample data with medium complexity",
            "metadata": {
                "version": "1.0",
                "type": "test"
            }
        }))
        .await
    });

    // Complex route - heavy processing simulation
    router.add_route("POST", "/api/v1/process", |mut req| async move {
        // Simulate complex processing
        sleep(Duration::from_millis(50)).await;

        // Parse request body
        let body_bytes = hyper::body::to_bytes(req.body_mut())
            .await
            .unwrap_or_default();

        let request_data: serde_json::Value = match serde_json::from_slice(&body_bytes) {
            Ok(data) => data,
            Err(_) => {
                return Response::builder()
                    .status(hyper::StatusCode::BAD_REQUEST)
                    .body(Body::from("Invalid request body"))
                    .unwrap();
            }
        };

        json_response(json!({
            "status": "processed",
            "timestamp": chrono::Utc::now(),
            "requestId": format!("req_{}", chrono::Utc::now().timestamp_nanos_opt().unwrap_or(0)),
            "processed": request_data
        }))
        .await
    });

    // Set up server
    let addr = SocketAddr::from(([127, 0, 0, 1], 3001));
    info!("Starting server on {}", addr);

    let make_svc = make_service_fn(move |_conn| {
        let router = router_clone.clone();
        async move {
            Ok::<_, Infallible>(service_fn(move |req| {
                handle_request(router.clone(), req)
            }))
        }
    });

    let server = Server::bind(&addr).serve(make_svc);

    // Run the server
    if let Err(e) = server.await {
        eprintln!("server error: {}", e);
    }
}
