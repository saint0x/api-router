use std::sync::Arc;
use std::time::{Duration, Instant};
use dashmap::DashMap;
use hyper::{Body, Request, Response, StatusCode};
use futures::future::BoxFuture;
use serde::Serialize;
use metrics::{counter, histogram};

type BoxedHandler = Box<dyn Fn(Request<Body>) -> BoxFuture<'static, Response<Body>> + Send + Sync>;

#[derive(Debug, Clone)]
pub struct RouteMetrics {
    pub route_match_time: Duration,
    pub handler_duration: Duration,
    pub total_request_time: Duration,
}

#[derive(Clone)]
pub struct Router {
    routes: Arc<DashMap<String, BoxedHandler>>,
}

impl Router {
    pub fn new() -> Self {
        Router {
            routes: Arc::new(DashMap::new()),
        }
    }

    pub fn add_route<F, Fut>(&self, method: &str, path: &str, handler: F)
    where
        F: Fn(Request<Body>) -> Fut + Send + Sync + 'static,
        Fut: std::future::Future<Output = Response<Body>> + Send + 'static,
    {
        let route_key = format!("{} {}", method, path);
        let boxed_handler = Box::new(move |req: Request<Body>| -> BoxFuture<'static, Response<Body>> {
            Box::pin(handler(req))
        });
        self.routes.insert(route_key, boxed_handler);
    }

    pub async fn handle_request(&self, req: Request<Body>) -> Response<Body> {
        let start_time = Instant::now();
        let route_match_start = Instant::now();

        // Create route key from method and path
        let route_key = format!("{} {}", req.method(), req.uri().path());
        
        // Attempt to find route handler
        let handler = self.routes.get(&route_key);
        let route_match_time = route_match_start.elapsed();

        match handler {
            Some(handler) => {
                counter!("requests_total", 1, "route" => route_key.clone());
                let handler_start = Instant::now();
                
                // Execute handler
                let response = handler(req).await;
                
                let handler_duration = handler_start.elapsed();
                let total_duration = start_time.elapsed();

                // Record metrics
                histogram!("route_match_time_seconds", route_match_time.as_secs_f64());
                histogram!("handler_duration_seconds", handler_duration.as_secs_f64());
                histogram!("total_request_time_seconds", total_duration.as_secs_f64());

                response
            }
            None => {
                counter!("requests_not_found", 1);
                Response::builder()
                    .status(StatusCode::NOT_FOUND)
                    .body(Body::from("Not Found"))
                    .unwrap()
            }
        }
    }
}

#[derive(Serialize)]
pub struct JsonResponse<T> {
    pub data: T,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

impl<T: Serialize> JsonResponse<T> {
    pub fn new(data: T) -> Self {
        Self {
            data,
            timestamp: chrono::Utc::now(),
        }
    }

    pub fn into_response(self) -> Response<Body> {
        match serde_json::to_vec(&self) {
            Ok(json) => Response::builder()
                .header("Content-Type", "application/json")
                .body(Body::from(json))
                .unwrap(),
            Err(_) => Response::builder()
                .status(StatusCode::INTERNAL_SERVER_ERROR)
                .body(Body::from("Internal Server Error"))
                .unwrap(),
        }
    }
}

// Helper function to create JSON responses
pub async fn json_response<T: Serialize>(data: T) -> Response<Body> {
    JsonResponse::new(data).into_response()
}

// Helper function to handle errors
pub fn error_response(status: StatusCode, message: &str) -> Response<Body> {
    Response::builder()
        .status(status)
        .body(Body::from(message.to_string()))
        .unwrap()
}
