# REST Pico W Lab Study Notes

## 1. Lab Overview
This lab builds a simple REST-style HTTP API on Raspberry Pi Pico W using MicroPython.
- Core files:
  - `main.py`: Wi-Fi connect, socket setup, server loop, sensor read, LED apply
  - `web_server.py`: HTTP parsing, route handling, response generation
- Main idea: expose sensor data and control actuator over HTTP endpoints.

## 2. Learning Outcomes
- Connect Pico W to Wi-Fi in STA mode.
- Run an HTTP server on port 80.
- Parse HTTP request method, path, headers, body.
- Implement route-based API behavior.
- Return suitable status codes and content types.
- Control onboard LED from POST request body.
- Return machine-readable JSON status for external clients.

## 3. System Architecture
1. Pico boots and connects to Wi-Fi.
2. Socket binds to `0.0.0.0:80` and listens.
3. For each client:
   - Read current internal temperature.
   - Read current LED state.
   - Pass request to `serve_client(...)`.
   - Apply returned LED command if present.

## 4. Endpoints in This Lab
- `GET /`
  - Returns API root page and endpoint summary.
- `GET /temp`
  - Returns current temperature.
- `POST /led`
  - Accepts LED state from request body and updates LED.
- `GET /status` (assignment extension)
  - Returns JSON containing temperature and current LED state.

## 5. Request Parsing Essentials
Typical parser extracts:
- HTTP method (GET, POST)
- Path (`/temp`, `/led`, `/status`)
- Headers (e.g., `Content-Type`)
- Body payload

Assumptions in this simple server:
- Small request payloads fit in initial `recv`.
- Basic parsing only, no full HTTP edge-case handling.

## 6. Response Essentials
A valid response includes:
- Status line: `HTTP/1.1 <status> <reason>`
- Headers: at least `Content-Type`, `Connection: close`
- Blank line
- Response body

Common statuses used:
- 200 OK
- 400 Bad Request
- 404 Not Found
- 405 Method Not Allowed

## 7. POST /led Body Formats
The server accepts LED state in multiple formats:
- JSON: `{ "state": 1 }`
- Form: `state=1`
- Plain text: `1`

Rules:
- Valid state is `0` or `1`.
- Invalid payload should return 400 Bad Request.

## 8. /status Assignment Requirement
`GET /status` must return JSON and include:
- `temperature` (numeric)
- `led_on` (boolean)

Expected Content-Type:
- `application/json`

Example:
```json
{
  "temperature": 24.55,
  "led_on": true
}
```

## 9. Main Loop State Flow
- `main.py` reads hardware state each request cycle.
- Passes current LED value into web handler.
- Handler returns LED command sentinel:
  - `-1`: no change
  - `0`: set OFF
  - `1`: set ON
- `main.py` is final authority that applies LED hardware update.

## 10. Common Mistakes
- Forgetting to set `Content-Type: application/json` for `/status`.
- Returning HTML instead of JSON for machine endpoint.
- Not passing LED current state into handler.
- Updating response body but not status code on errors.
- Accepting malformed body without validation.
- Not handling unsupported method with 405.
- Missing fallback route for unknown paths (404).

## 11. Testing Checklist (Postman)
1. `POST /led` with `{ "state": 1 }` -> LED turns ON.
2. `GET /status` -> `200`, JSON valid, `led_on: true`.
3. `POST /led` with `{ "state": 0 }` -> LED turns OFF.
4. `GET /status` -> `led_on: false`.
5. `GET /temp` -> numeric temperature shown.
6. Invalid `POST /led` body -> `400 Bad Request`.
7. Wrong method on route -> `405 Method Not Allowed`.
8. Unknown path -> `404 Not Found`.

## 12. Viva One-Liners
- REST endpoint behavior is determined by method + path.
- JSON endpoints are for machine-to-machine readability.
- 405 means path exists but method is wrong.
- 404 means path is unknown.
- Input validation prevents malformed requests from crashing logic.
- Separate networking/router logic from hardware-control loop for clarity.
