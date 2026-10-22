package httpjson

import (
	"encoding/json"
	"io"
	"net/http"
)

const maxBodyBytes = 1 << 20

type errorBody struct {
	Code    string `json:"code"`
	Message string `json:"message"`
}

func Write(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	// The status is already sent, so a failed write means the client went away.
	_ = json.NewEncoder(w).Encode(body)
}

func Error(w http.ResponseWriter, status int, code, message string) {
	Write(w, status, errorBody{Code: code, Message: message})
}

// Read decodes a JSON request body. Unknown fields are ignored, so newer
// clients can send fields that this version does not know yet.
func Read(r *http.Request, into any) error {
	return json.NewDecoder(io.LimitReader(r.Body, maxBodyBytes)).Decode(into)
}
