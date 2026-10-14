package app

import "os"

// Config is read from the environment. This is the one composition file
// where control flow is allowed.
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
