# REST Pico W Lab MCQ Questions and Answers

## Section A: Core MCQs

<ol>
  <li>The primary purpose of `main.py` in this lab is to:<br>
    A. Parse JSON only<br>
    B. Manage Wi-Fi, socket loop, and hardware state updates<br>
    C. Provide BLE services<br>
    D. Compile static web pages
  </li>
  <li>The primary purpose of `web_server.py` is to:<br>
    A. Read ADC continuously only<br>
    B. Handle HTTP parsing, routing, and response creation<br>
    C. Configure USB mass storage<br>
    D. Control PWM audio
  </li>
  <li>The server listens on which port by default in this lab?<br>
    A. 21<br>
    B. 80<br>
    C. 1883<br>
    D. 443
  </li>
  <li>The endpoint that returns current temperature is typically:<br>
    A. GET /status<br>
    B. POST /temp<br>
    C. GET /temp<br>
    D. PUT /temp
  </li>
  <li>The endpoint used to control LED state is:<br>
    A. GET /led<br>
    B. POST /led<br>
    C. DELETE /led<br>
    D. PATCH /led
  </li>
  <li>If a client uses GET on `/led` but the route expects POST, correct status is:<br>
    A. 200<br>
    B. 404<br>
    C. 405<br>
    D. 500
  </li>
  <li>Unknown route should return:<br>
    A. 201<br>
    B. 400<br>
    C. 405<br>
    D. 404
  </li>
  <li>For assignment route `/status`, expected content type is:<br>
    A. text/html<br>
    B. application/json<br>
    C. text/plain only<br>
    D. multipart/form-data
  </li>
  <li>Which field should represent LED state in `/status` response?<br>
    A. led_pin<br>
    B. led_value_raw<br>
    C. led_on (boolean)<br>
    D. led_port
  </li>
  <li>Why is `json.dumps(...)` used for `/status`?<br>
    A. To connect Wi-Fi<br>
    B. To convert Python dict into JSON string
    C. To open socket
    D. To parse URL path
  </li>
  <li>Which body is valid for turning LED on in JSON mode?<br>
    A. {"state":"on"}<br>
    B. {"state":1}<br>
    C. {"led":true,"x":9}<br>
    D. {"value":"high"}
  </li>
  <li>In this lab flow, hardware LED update is finally applied by:<br>
    A. HTTP client browser<br>
    B. main loop after interpreting returned state<br>
    C. DNS server<br>
    D. Thonny editor
  </li>
  <li>What does `0.0.0.0` bind address mean here?<br>
    A. Listen only on localhost<br>
    B. Listen on all network interfaces<br>
    C. Disable network stack<br>
    D. Connect to default gateway
  </li>
  <li>A 400 Bad Request on `/led` most likely means:<br>
    A. Wi-Fi disconnected
    B. Route not implemented
    C. Request body/state format invalid<br>
    D. Wrong IP subnet mask
  </li>
  <li>Why pass current LED state into `serve_client(...)` for `/status`?
    A. So server can report actual runtime actuator state
    B. To speed Wi-Fi handshake
    C. To reduce ADC noise
    D. To avoid socket bind
  </li>
  <li>What is the benefit of separating `main.py` and `web_server.py`?
    A. Reduces code readability
    B. Clean separation of hardware loop and HTTP routing logic
    C. Prevents use of status codes
    D. Removes need for parsing
  </li>
  <li>The Pico W temperature value in this lab comes from:
    A. External DHT22 only
    B. ADC read of internal temperature sensor path
    C. HTTP header
    D. Wi-Fi RSSI
  </li>
  <li>If route exists but method is unsupported, which is correct?
    A. 404
    B. 302
    C. 405
    D. 418
  </li>
  <li>The expected `/status` JSON includes:
    A. humidity and pressure only
    B. temperature and led_on
    C. ip and mac only
    D. ssid and password
  </li>
  <li>Why validate LED state to only 0/1?
    A. To minimize flash usage only
    B. To enforce deterministic actuator behavior and reject malformed input
    C. To increase TCP window size
    D. To avoid JSON parsing
  </li>
</ol>

### Answers: Section A
<ol>
  <li>B</li>
  <li>B</li>
  <li>B</li>
  <li>C</li>
  <li>B</li>
  <li>C</li>
  <li>D</li>
  <li>B</li>
  <li>C</li>
  <li>B</li>
  <li>B</li>
  <li>B</li>
  <li>B</li>
  <li>C</li>
  <li>A</li>
  <li>B</li>
  <li>B</li>
  <li>C</li>
  <li>B</li>
  <li>B</li>
</ol>

## Section B: Harder Scenario MCQs

<ol start="21">
  <li>`GET /status` returns HTML but should be JSON. Most direct fix is:<br>
    A. Change port to 443<br>
    B. Build dict, `json.dumps`, and return with `content_type="application/json"`<br>
    C. Remove LED endpoint
    D. Switch to BLE notifications
  </li>
  <li>`POST /led` returns 200 but physical LED does not change. Most likely architecture issue:<br>
    A. Browser cache problem
    B. main loop does not apply returned LED state to hardware
    C. Wrong DNS record
    D. Missing root route
  </li>
  <li>Client gets 405 on `/temp`. Interpretation:<br>
    A. Path exists, method used is not allowed for that path
    B. Path does not exist
    C. JSON is invalid
    D. Socket is closed permanently
  </li>
  <li>JSON payload `{ "state": "1" }` is sent. Robust parser behavior should:
    A. Reject all string values always
    B. Optionally coerce "1" to int if explicitly supported
    C. Turn LED on and off simultaneously
    D. Return 404
  </li>
  <li>Server handles only first request then appears stuck. Most plausible low-level cause:
    A. Socket not listening
    B. Client socket not closed in handler path
    C. Temperature conversion too accurate
    D. Missing SSID
  </li>
  <li>Unknown path returns 200 with root page. Why is this undesirable?
    A. It hides routing errors; correct behavior should be explicit 404
    B. It improves API discoverability
    C. It is required by REST
    D. It prevents timeout
  </li>
  <li>Assignment asks `led_on` boolean in `/status`, but code returns `0/1` numeric. Best fix:
    A. Keep as integer; booleans are invalid JSON
    B. Convert to Python bool before JSON serialization
    C. Convert to string "true"/"false" manually always
    D. Remove LED field
  </li>
  <li>Malformed `/led` payload causes unhandled exception and crash. Best defensive improvement:
    A. Wrap parse in validation + exception handling and return 400
    B. Remove request body support
    C. Force reboot after each request
    D. Ignore all POST requests
  </li>
  <li>Two clients send rapid `/led` POST requests with opposite values. Most accurate statement:
    A. Last successfully processed request determines final LED state
    B. First request is always permanent
    C. Pico automatically merges states
    D. HTTP forbids concurrent updates
  </li>
  <li>If `/status` should reflect actual LED state, the value should be sourced from:
    A. Last request body only
    B. Hardware read/current runtime LED value passed from main loop
    C. Wi-Fi driver statistics
    D. Socket peer address
  </li>
  <li>Returning 500 for user input validation failures is poor practice because:
    A. 500 indicates server fault, not client request format issues
    B. 500 is faster than 400
    C. 500 enables better parsing
    D. 500 is required for POST
  </li>
  <li>If content type is `application/x-www-form-urlencoded`, expected LED body shape is typically:
    A. `{state:1}`
    B. `state=1`
    C. `<state>1</state>`
    D. `LED ON`
  </li>
  <li>Main loop catches OSError and continues. Primary benefit:
    A. Keeps server resilient to transient connection/socket errors
    B. Avoids all parsing code
    C. Eliminates need for status codes
    D. Forces non-blocking mode automatically
  </li>
  <li>Best quick end-to-end verification for assignment requirement:
    A. Only open `/` in browser
    B. POST `/led` then GET `/status` and verify JSON + LED truth value match
    C. Restart Pico after each request
    D. Disable Wi-Fi encryption
  </li>
  <li>Most accurate split of responsibilities:
    A. `web_server.py` handles hardware writes; `main.py` handles HTML only
    B. `main.py` orchestrates hardware and loop; `web_server.py` handles HTTP request/response routing
    C. Both files do identical work
    D. `main.py` is optional
  </li>
</ol>

### Answers: Section B
<ol start="21">
  <li>B</li>
  <li>B</li>
  <li>A</li>
  <li>B</li>
  <li>B</li>
  <li>A</li>
  <li>B</li>
  <li>A</li>
  <li>A</li>
  <li>B</li>
  <li>A</li>
  <li>B</li>
  <li>A</li>
  <li>B</li>
  <li>B</li>
</ol>
