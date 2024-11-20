package router

import (
	"net/http"
	"sync"
	"time"
)

// Metrics holds timing information for request processing
type Metrics struct {
	RouteMatchTime    time.Duration
	HandlerStartTime  time.Time
	HandlerEndTime    time.Time
	TotalRequestTime  time.Duration
}

// MetricsChannel is used to send metrics data
type MetricsChannel chan Metrics

// Route represents a route node in our high-performance trie structure
type Route struct {
	children map[string]*Route
	handler  http.HandlerFunc
	path     string
}

// Router is our high-performance router implementation
type Router struct {
	root     *Route
	pool     *sync.Pool
	Metrics  MetricsChannel
}

// New creates a new optimized router instance
func New() *Router {
	r := &Router{
		root: &Route{
			children: make(map[string]*Route),
		},
		Metrics: make(MetricsChannel, 10000), // Buffered channel for metrics
	}

	// Initialize sync.Pool for metrics to reduce allocations
	r.pool = &sync.Pool{
		New: func() interface{} {
			return &Metrics{}
		},
	}

	return r
}

// Handle registers a new route with the router
func (r *Router) Handle(method, path string, handler http.HandlerFunc) {
	current := r.root
	parts := splitPath(path)

	for _, part := range parts {
		if current.children[part] == nil {
			current.children[part] = &Route{
				children: make(map[string]*Route),
				path:     part,
			}
		}
		current = current.children[part]
	}
	
	if current.handler != nil {
		panic("Route already exists: " + path)
	}
	current.handler = handler
}

// ServeHTTP implements the http.Handler interface
func (r *Router) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	startTime := time.Now()
	
	// Get metrics instance from pool
	metrics := r.pool.Get().(*Metrics)
	defer r.pool.Put(metrics)

	// Reset metrics
	*metrics = Metrics{}
	
	// Find route
	routeMatchStart := time.Now()
	handler, found := r.findRoute(req.URL.Path)
	metrics.RouteMatchTime = time.Since(routeMatchStart)

	if !found {
		http.NotFound(w, req)
		return
	}

	// Execute handler with timing
	metrics.HandlerStartTime = time.Now()
	handler(w, req)
	metrics.HandlerEndTime = time.Now()
	metrics.TotalRequestTime = time.Since(startTime)

	// Send metrics asynchronously
	select {
	case r.Metrics <- *metrics:
	default:
		// Channel full, metrics dropped
	}
}

// findRoute locates the appropriate handler for a given path
func (r *Router) findRoute(path string) (http.HandlerFunc, bool) {
	current := r.root
	parts := splitPath(path)

	for _, part := range parts {
		if next, ok := current.children[part]; ok {
			current = next
		} else {
			return nil, false
		}
	}

	if current.handler == nil {
		return nil, false
	}

	return current.handler, true
}

// splitPath splits a path into parts, optimized for minimal allocations
func splitPath(path string) []string {
	if path == "/" {
		return []string{"/"}
	}

	parts := make([]string, 0, 8) // Pre-allocate for common case
	start := 0
	for i := 1; i < len(path); i++ {
		if path[i] == '/' {
			if start < i {
				parts = append(parts, path[start:i])
			}
			start = i
		}
	}
	
	if start < len(path) {
		parts = append(parts, path[start:])
	}

	return parts
}
