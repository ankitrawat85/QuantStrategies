# Run all three methods with a snapshot (no plot)

python trendline_stream_run_all.py \
 --script ./trendline_stream_tlc_like_hough_cfg.py \
 --csv data_SBIN.csv \
 --config tlc_config_methods.json \
 --methods ols,huber,hough \
 --snapshot-date 2022-06-27 \
 --snapshot-only \
 --outdir ./out \
 --min-confidence 0.70

# Run hough+huber with plots and a time window, then combine events

python trendline_stream_run_all.py \
 --script ./trendline_stream_tlc_like_hough_cfg.py \
 --csv data_SBIN.csv \
 --config tlc_config_methods.json \
 --methods hough,huber \
 --x-start 2022-01-01 \
 --x-end 2023-08-01 \
 --plot \
 --min-confidence 0.70 \
 --combine \
 --outdir ./out

nkit@Ankits-MacBook-Pro Latest_Hough_merge_tlc % python trendline_stream_run_all.py \
 --script ./trendline_stream_tlc_like_hough_cfg.py \
 --csv data_SBIN.csv \
 --config tlc_config_methods.json \
 --methods ols,hough,huber \
 --x-start 2022-01-01 \
 --x-end 2023-08-01 \
 --plot \
 --min-confidence 0.70 \
 --combine \
 --outdir ./out

ankit@Ankits-MacBook-Pro Latest_Hough_merge_tlc % python trendline_stream_run_all.py \
 --script ./trendline_stream_tlc_like_hough_cfg.py \
 --csv ./data_SBIN.csv \
 --config ./tlc_config_methods_fixed.json \
 --x-start 2022-01-01 \
 --x-end 2025-08-01 \
 --plot \
 --min-confidence 0.70 \
 --combine \
 --outdir ./out

python trendline_stream_run_all.py \
 --script main_trendline_stream.py \
 --csv data_SBIN.csv \
 --config tlc_config_methods.json \
 --methods ols,huber,hough,ols_env \
 --outdir ./out_results \
 --plot \
 --combine \
 --passthrough "--env-mode atr --env-base 14 --env-k 2.0"

python sbin_strength_plots.py \
 --ohlc data_SBIN.csv \
 --ols data_SBIN_ols_env_events.csv \
 --huber data_SBIN_huber_events.csv \
 --hough data_SBIN_hough_events.csv \
 --outdir out \
 --conf-min 0.80

# Use both new methods together

python sbin_strength_plots.py \
 --ohlc data_SBIN.csv \
 --ols ols_breaks.csv \
 --huber huber_breaks.csv \
 --hough hough_breaks.csv \
 --ols-shift-min ols_shift_min_breaks.csv \
 --ols-envelop ols_envelop_breaks.csv \
 --outdir out

python trendline_stream_run_all.py \
 --script main_trendline_stream.py \
 --csv data_SBIN.csv \
 --config tlc_config_methods.json \
 --x-start 2022-01-01 \
 --x-end 2025-08-01 \
 --methods ols,huber,hough,ols_shift_min,ols_envelop \
 --outdir ./out_results \
 --plot \
 --combine \
 --passthrough "--env-mode atr --env-base 14 --env-k 2.0"

python strength_plots.py \
 --ohlc data_SBIN.csv \
 --ols ./out_results/data_SBIN_ols_events.csv \
 --huber ./out_results/data_SBIN_huber_events.csv \
 --hough ./out_results/data_SBIN_hough_events.csv \
 --ols-shift-min ./out_results/data_SBIN_ols_shift_min_events.csv \
 --ols-envelop ./out_results/data_SBIN_ols_envelop_events.csv \
 --outdir out \
 --conf-min 0.80

python trendline_stream_run_all.py \
 --script main_trendline_stream.py \
 --csv data_SBIN.csv \
 --config tlc_config_methods.json \
 --x-start 2022-01-01 \
 --x-end 2025-08-01 \
 --methods ols,huber,hough,ols_shift_min,ols_envelop \
 --outdir ./out_results \
 --plot \
 --combine \
 --passthrough "--env-mode atr --env-base 14 --env-k 2.0"

python trendline_stream_run_all_consolidated.py \
 --script main_trendline_stream.py \
 --csv data_SBIN.csv \
 --config tlc_config_methods.json \
 --methods ols,huber,hough,ols_shift_min,ols_envelop \
 --snapshot-date 2022-06-27 \
 --snapshot-only \
 --outdir ./out \
 --signals-summary-out ./out/SBIN_signals_summary
--conf-min 0.80

python trendline_stream_run_all.py \
 --script main_trendline_stream.py \
 --csv data_SBIN.csv \
 --config tlc_config_methods.json \
 --methods ols,huber,hough,ols_shift_min,ols_envelop \
 --outdir ./out \
 --signals-summary-out ./out/SBIN_signals_summary \
 --min-confidence 0.70

python trendline_stream_run_all.py \
 --script main_trendline_stream.py \
 --csv data_SBIN.csv \
 --config tlc_config_methods.json \
 --x-start 2022-01-01 \
 --x-end 2025-08-01 \
 --methods ols,huber,hough,ols_shift_min,ols_envelop \
 --outdir ./out_results \
 --plot \
 --combine \

--passthrough "--env-mode atr --env-base 14 --env-k 2.0"

python trendline_stream_run_all-2.py \
 --script main_trendline_stream.py \
 --csv data_SBIN.csv \
 --config tlc_config_methods.json \
 --methods ols,huber,hough,ols_shift_min,ols_envelop \
 --outdir ./out_angle0 \
 --signals-summary-out ./SBIN_signals_summary_angle0 \
 --min-confidence 0.00

python trendline_stream_run_all.py \
 --script main_trendline_stream.py \
 --csv data_INFY.csv \
 --config tlc_config_methods.json \
 --methods ols \
 --outdir ./out_angle0 \
 --signals-summary-out ./SBIN_signals_summary_angle0 \
 --min-confidence 0.0 \
 --x-start 2022-01-01 \
 --x-end 2025-07-30 \
 --max-angle-deg 90
