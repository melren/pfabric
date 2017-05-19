# From the paper: 
# Disable newer mechanisms in TCP such as fast retransmit, dup-ACKs, timeout estimation
# Flows start with a large window size (at least a BDP) and window undergoes normal AI
# Decreases only occur upon timeout

sysctl -w net.ipv4.tcp_allowed_congestion_control="reno"
sysctl -w net.ipv4.tcp_app_win=31
sysctl -w net.ipv4.tcp_available_congestion_control="reno"
sysctl -w net.ipv4.tcp_congestion_control="reno"
sysctl -w net.ipv4.tcp_dsack=0
sysctl -w net.ipv4.tcp_early_retrans=0
sysctl -w net.ipv4.tcp_ecn=0
sysctl -w net.ipv4.tcp_fack=0
sysctl -w net.ipv4.tcp_fastopen=0
sysctl -w net.ipv4.tcp_frto=0
sysctl -w net.ipv4.tcp_rfc1337=0
sysctl -w net.ipv4.tcp_sack=0
sysctl -w net.ipv4.tcp_slow_start_after_idle=0
sysctl -w net.ipv4.tcp_syncookies=0
sysctl -w net.ipv4.tcp_timestamps=1
sysctl -w net.ipv4.tcp_window_scaling=1
