package app

import "os"

type Config struct {
	Addr    string
	DataDir string
}

func ConfigFromEnvironment() Config {
	return Config{
		Addr:    valueOr(os.Getenv("ADDR"), ":8080"),
		DataDir: valueOr(os.Getenv("DATA_DIR"), "data"),
	}
}

func valueOr(value, fallback string) string {
	if value == "" {
		return fallback
	}
	return value
}
