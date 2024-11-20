package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"runtime"
	"time"

	"api-router/pkg"
)

type Response struct {
	Message string    `json:"message"`
	Time    time.Time `json:"time"`
}

func main() {
	// Optimize for maximum performance
	runtime.GOMAXPROCS(runtime.NumCPU())

	router := router.New()

	// Simple route - baseline performance test
	router.Handle("GET", "/ping", func(w http.ResponseWriter, r *http.Request) {
		json.NewEncoder(w).Encode(Response{
			Message: "pong",
			Time:    time.Now(),
		})
	})

	// Medium complexity route - simulates typical API endpoint
	router.Handle("GET", "/api/v1/data", func(w http.ResponseWriter, r *http.Request) {
		// Simulate some processing
		time.Sleep(time.Millisecond * 10)
		
		data := map[string]interface{}{
			"id":        123,
			"timestamp": time.Now(),
			"data":      "Sample data with medium complexity",
			"metadata": map[string]interface{}{
				"version": "1.0",
				"type":    "test",
			},
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(data)
	})

	// Complex route - heavy processing simulation
	router.Handle("POST", "/api/v1/process", func(w http.ResponseWriter, r *http.Request) {
		// Simulate complex processing
		time.Sleep(time.Millisecond * 50)
		
		var requestData map[string]interface{}
		if err := json.NewDecoder(r.Body).Decode(&requestData); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		result := map[string]interface{}{
			"status":     "processed",
			"timestamp":  time.Now(),
			"requestId":  fmt.Sprintf("req_%d", time.Now().UnixNano()),
			"processed": requestData,
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(result)
	})

	// Start metrics collection
	go func() {
		for metric := range router.Metrics {
			log.Printf("Route Match: %v, Handler Time: %v, Total Time: %v\n",
				metric.RouteMatchTime,
				metric.HandlerEndTime.Sub(metric.HandlerStartTime),
				metric.TotalRequestTime)
		}
	}()

	log.Println("Starting server on :3000")
	if err := http.ListenAndServe(":3000", router); err != nil {
		log.Fatal(err)
	}
}
