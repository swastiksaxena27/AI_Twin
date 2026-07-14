# ROLE

You are responsible for the Agent Layer.

Work ONLY inside: `agent/`

## Responsibilities

Keyboard collection, Mouse collection, Process monitoring, USB monitoring, Download monitoring, Network monitoring, Feature extraction

Generate one feature vector every 30 seconds.

## Frozen Features

ks_dwell_mean, ks_dwell_std, ks_flight_mean, ks_flight_std, ks_wpm, ks_error_rate, ms_speed_mean, ms_speed_std, ms_click_rate, ms_idle_ratio, ap_unique_count, ap_unknown_flag

Never store typed text. Only store timings and metadata.
Use: psutil, pynput, watchdog. Add logging and exception handling.
