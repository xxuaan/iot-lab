# BLE Pico W Lab MCQ Questions and Answers

## Section A: Core MCQs

<ol>
  <li>In this lab, the board that advertises and hosts GATT data is the:<br>
    A. Observer<br>
    B. Broadcaster-only<br>
    C. Peripheral<br>
    D. Scanner
  </li>
  <li>The board that scans and initiates connection is the:<br>
    A. Peripheral<br>
    B. Central<br>
    C. Beacon<br>
    D. GATT server only
  </li>
  <li>The custom service UUID used is:<br>
    A. 0x1A00<br>
    B. 0x1A01<br>
    C. 0x1A02<br>
    D. 0x2902
  </li>
  <li>The LED characteristic UUID is:<br>
    A. 0x1A00<br>
    B. 0x1A01<br>
    C. 0x1A02<br>
    D. 0x180A
  </li>
  <li>The status characteristic supports:<br>
    A. WRITE only<br>
    B. READ and NOTIFY<br>
    C. NOTIFY only<br>
    D. INDICATE only
  </li>
  <li>Why is CCCD needed?<br>
    A. To discover services<br>
    B. To encrypt packets<br>
    C. To configure notifications and indications<br>
    D. To set advertising interval
  </li>
  <li>Value to enable notifications is:<br>
    A. 0x0001<br>
    B. 0x0100<br>
    C. 0x1000<br>
    D. 0xFFFF
  </li>
  <li>A likely reason notify fails while read works is:<br>
    A. Client did not write CCCD<br>
    B. RSSI too strong<br>
    C. Service UUID too short<br>
    D. Pull-up resistor enabled
  </li>
  <li>Button debounce is used to:<br>
    A. Increase BLE range<br>
    B. Prevent repeated false presses<br>
    C. Improve UUID matching<br>
    D. Force reconnect
  </li>
  <li>Characteristic discovery should happen:<br>
    A. Before scan<br>
    B. After successful connect and service discovery<br>
    C. Only after disconnect<br>
    D. Only on server
  </li>
  <li>Correct Task 4 path is:<br>
    A. Client write -> server write IRQ -> server LED update<br>
    B. Server notify -> client write<br>
    C. Client read -> server disconnect<br>
    D. CCCD write -> LED toggles
  </li>
  <li>Notify is often better than polling because:<br>
    A. No stack needed<br>
    B. Server pushes updates only when needed<br>
    C. UUID is not required<br>
    D. It disables interrupts
  </li>
  <li>On disconnect, server should:<br>
    A. Stop BLE forever<br>
    B. Re-advertise<br>
    C. Delete service<br>
    D. Reset board
  </li>
  <li>BLE logic in this lab is mostly:<br>
    A. Event driven using IRQ callbacks<br>
    B. Blocking synchronous only<br>
    C. Interrupt disabled loops<br>
    D. File system driven
  </li>
  <li>A practical recovery when discovery fails is:<br>
    A. Guess random handles<br>
    B. Disconnect and retry cleanly<br>
    C. Disable notifications permanently<br>
    D. Change ADC pin
  </li>
  <li>Beacon mode differs because beacon:<br>
    A. Never advertises<br>
    B. Advertises only and does not run connectable GATT exchange<br>
    C. Requires Wi-Fi<br>
    D. Uses only write requests
  </li>
  <li>CCCD UUID is:<br>
    A. 0x2A00<br>
    B. 0x2800<br>
    C. 0x2902<br>
    D. 0x180D
  </li>
  <li>BLE handle usually refers to:<br>
    A. Pin number<br>
    B. ATT attribute index<br>
    C. Device name pointer<br>
    D. RSSI threshold
  </li>
  <li>If target name filter mismatches, client likely:<br>
    A. Still connects to target<br>
    B. Fails to find intended server<br>
    C. Enables notify anyway<br>
    D. Skips scan stage
  </li>
  <li>Why avoid hardcoded handles?<br>
    A. Handles are encrypted<br>
    B. Runtime layout can change handle values<br>
    C. Handles are Wi-Fi specific<br>
    D. Handles are random each packet
  </li>
  <li>Read flow requires:<br>
    A. gattc_read plus read result/done events<br>
    B. CCCD write only<br>
    C. gap_advertise call<br>
    D. Service registration on client
  </li>
  <li>WRITE_NO_RESPONSE is useful when:<br>
    A. Lowest overhead and low latency are preferred<br>
    B. Maximum acknowledgment is required<br>
    C. Read is disabled<br>
    D. Scan is disabled
  </li>
  <li>Server notify targets:<br>
    A. All relevant active connection handles<br>
    B. Only first client forever<br>
    C. No clients unless scanning<br>
    D. Only disconnected clients
  </li>
  <li>Robust write handling should:<br>
    A. Crash on parse errors<br>
    B. Validate and safely handle malformed values<br>
    C. Ignore all writes<br>
    D. Disable LED updates
  </li>
  <li>LED state value format in this lab is generally:<br>
    A. float32 binary<br>
    B. UTF-8 bytes for 0 or 1<br>
    C. encrypted JSON only<br>
    D. UUID text
  </li>
</ol>

### Answers: Section A
<ol>
  <li>C</li>
  <li>B</li>
  <li>C</li>
  <li>A</li>
  <li>B</li>
  <li>C</li>
  <li>B</li>
  <li>A</li>
  <li>B</li>
  <li>B</li>
  <li>A</li>
  <li>B</li>
  <li>B</li>
  <li>A</li>
  <li>B</li>
  <li>B</li>
  <li>C</li>
  <li>B</li>
  <li>B</li>
  <li>B</li>
  <li>A</li>
  <li>A</li>
  <li>A</li>
  <li>B</li>
  <li>B</li>
</ol>

## Section B: Harder Scenario MCQs

<ol start="26">
  <li>Client logs show service found and characteristics found, but no notify events appear. Most probable direct cause is:<br>
    A. Wrong advertising interval<br>
    B. CCCD was not written successfully<br>
    C. LED characteristic is read only<br>
    D. Client scan window too small
  </li>
  <li>Client reads LED correctly but writes do nothing on server. Most likely issue is:<br>
    A. Wrong LED characteristic handle used for write path<br>
    B. Status string decode failed<br>
    C. Client button debounce too high<br>
    D. ADC formula is incorrect
  </li>
  <li>Server disconnect event happens and client cannot reconnect unless server is reset. Most likely missing logic:<br>
    A. Re-register services<br>
    B. Re-enable ADC<br>
    C. Re-start advertising on disconnect<br>
    D. Rebuild UUID objects
  </li>
  <li>Client found target name, connected, then disconnected after service discovery done with no target service found. Most likely explanation:<br>
    A. Service UUID mismatch between server and client<br>
    B. RSSI too low for read<br>
    C. Status characteristic not notifiable<br>
    D. LED write mode set to no response
  </li>
  <li>Descriptor discovery returns no CCCD, and client uses status_handle plus 1 fallback. Primary risk is:<br>
    A. Battery drain only<br>
    B. Writing to wrong attribute if layout assumptions are false<br>
    C. Device name corruption<br>
    D. Duplicate advertising packets
  </li>
  <li>User presses Button B once but server toggles LED multiple times. Most likely immediate fix:<br>
    A. Decrease MTU size<br>
    B. Add or improve button debounce logic<br>
    C. Disable notifications<br>
    D. Increase advertising payload size
  </li>
  <li>Server crashes occasionally on incoming writes from unknown clients. Most robust coding improvement:<br>
    A. Add try/except and range validation on parsed LED value<br>
    B. Disable write support<br>
    C. Remove IRQ handler<br>
    D. Only allow reads
  </li>
  <li>In a multi-client future extension, server stores one conn_handle only. Likely issue:<br>
    A. Only one client may receive notifications correctly<br>
    B. UUID conflict at boot<br>
    C. Service registration fails immediately<br>
    D. Client scan cannot stop
  </li>
  <li>Client receives notify on unexpected handle and ignores data. Correct interpretation:<br>
    A. Bug in BLE hardware<br>
    B. Handler should verify the handle map from discovery and match correctly<br>
    C. Advertising packet malformed<br>
    D. ADC channel unavailable
  </li>
  <li>Client starts scanning indefinitely and never connects even though server is present. Most diagnostic first step:<br>
    A. Verify target name in scan filter matches actual advertised name exactly<br>
    B. Change button pin numbers<br>
    C. Disable status characteristic<br>
    D. Force CCCD write before connect
  </li>
  <li>Why might WRITE_NO_RESPONSE be selected for LED control in this lab?<br>
    A. It can reduce transaction overhead for simple state updates<br>
    B. It guarantees stronger delivery semantics than write with response<br>
    C. It enables notifications automatically<br>
    D. It bypasses service discovery
  </li>
  <li>Client local LED toggles immediately on button write, but server LED remains unchanged due to failed write. Best UI improvement:<br>
    A. Update local LED only after write success callback<br>
    B. Remove local LED usage entirely<br>
    C. Toggle local LED twice<br>
    D. Increase sleep delay
  </li>
  <li>Notify path works once, then not again after reconnect. Most likely design oversight:<br>
    A. CCCD subscription was not re-established on new connection<br>
    B. Service UUID became invalid<br>
    C. ADC conversion changed MTU<br>
    D. Scan interval too short
  </li>
  <li>In event-driven BLE code, race conditions are reduced by:<br>
    A. Assuming event order never changes<br>
    B. Tracking connection and handle state explicitly and checking before actions<br>
    C. Removing all callbacks<br>
    D. Forcing fixed delays only
  </li>
  <li>Which statement best captures read result versus read done semantics?<br>
    A. Both carry identical payload always<br>
    B. Read result carries value data; read done indicates operation completion status<br>
    C. Read done always arrives first<br>
    D. Read result is only for notify
  </li>
</ol>

### Answers: Section B
<ol start="26">
  <li>B</li>
  <li>A</li>
  <li>C</li>
  <li>A</li>
  <li>B</li>
  <li>B</li>
  <li>A</li>
  <li>A</li>
  <li>B</li>
  <li>A</li>
  <li>A</li>
  <li>A</li>
  <li>A</li>
  <li>B</li>
  <li>B</li>
</ol>

