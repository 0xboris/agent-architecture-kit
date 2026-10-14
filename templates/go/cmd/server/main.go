package main

import (
	"log"
	"net/http"
	"os"

	"__GO_MODULE__/internal/app"
)

func main() {
	config := app.ConfigFromEnvironment()
	service := app.New(app.LiveDependencies(config, os.Stderr))
	log.Printf("listening on %s", config.Addr)
	if err := http.ListenAndServe(config.Addr, service.Handler()); err != nil {
		log.Fatal(err)
	}
}
