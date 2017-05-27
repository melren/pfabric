# Resets the default settings of TCP on Linux Debian 8 Jessie
# These are copied from listing sysctl variables currently on the system

sysctl -w net.ipv4.tcp_abort_on_overflow=0
sysctl -w net.ipv4.tcp_adv_win_scale=1
sysctl -w net.ipv4.tcp_allowed_congestion_control="cubic reno"
sysctl -w net.ipv4.tcp_app_win=31
sysctl -w net.ipv4.tcp_autocorking=1
sysctl -w net.ipv4.tcp_available_congestion_control="cubic reno"
sysctl -w net.ipv4.tcp_base_mss=512
sysctl -w net.ipv4.tcp_challenge_ack_limit=1000
sysctl -w net.ipv4.tcp_congestion_control="cubic"
sysctl -w net.ipv4.tcp_dsack=1
sysctl -w net.ipv4.tcp_early_retrans=3
sysctl -w net.ipv4.tcp_ecn=2
sysctl -w net.ipv4.tcp_fack=1
sysctl -w net.ipv4.tcp_fastopen=1
sysctl -w net.ipv4.tcp_fastopen_key="00000000-00000000-00000000-00000000"
sysctl -w net.ipv4.tcp_fin_timeout=60
sysctl -w net.ipv4.tcp_frto=2
sysctl -w net.ipv4.tcp_fwmark_accept=0
sysctl -w net.ipv4.tcp_keepalive_intvl=75
sysctl -w net.ipv4.tcp_keepalive_probes=9
sysctl -w net.ipv4.tcp_keepalive_time=7200
sysctl -w net.ipv4.tcp_limit_output_bytes=131072
sysctl -w net.ipv4.tcp_low_latency=0
sysctl -w net.ipv4.tcp_max_orphans=32768
sysctl -w net.ipv4.tcp_max_syn_backlog=256
sysctl -w net.ipv4.tcp_max_tw_buckets=32768
sysctl -w net.ipv4.tcp_min_tso_segs=2
sysctl -w net.ipv4.tcp_moderate_rcvbuf=1
sysctl -w net.ipv4.tcp_mtu_probing=0
sysctl -w net.ipv4.tcp_no_metrics_save=0
sysctl -w net.ipv4.tcp_notsent_lowat=-1
sysctl -w net.ipv4.tcp_orphan_retries=0
sysctl -w net.ipv4.tcp_reordering=3
sysctl -w net.ipv4.tcp_retrans_collapse=1
sysctl -w net.ipv4.tcp_retries1=3
sysctl -w net.ipv4.tcp_retries2=15
sysctl -w net.ipv4.tcp_rfc1337=1
sysctl -w net.ipv4.tcp_sack=1
sysctl -w net.ipv4.tcp_slow_start_after_idle=1
sysctl -w net.ipv4.tcp_stdurg=0
sysctl -w net.ipv4.tcp_syn_retries=6
sysctl -w net.ipv4.tcp_synack_retries=5
sysctl -w net.ipv4.tcp_syncookies=1
sysctl -w net.ipv4.tcp_thin_dupack=0
sysctl -w net.ipv4.tcp_thin_linear_timeouts=0
sysctl -w net.ipv4.tcp_timestamps=1
sysctl -w net.ipv4.tcp_tso_win_divisor=3
sysctl -w net.ipv4.tcp_tw_recycle=0
sysctl -w net.ipv4.tcp_tw_reuse=0
sysctl -w net.ipv4.tcp_window_scaling=1
sysctl -w net.ipv4.tcp_workaround_signed_windows=0