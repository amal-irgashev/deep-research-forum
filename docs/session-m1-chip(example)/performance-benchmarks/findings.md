## Round 1 Findings
Timestamp: 2025-11-13T18:57:02Z

Lens: Performance Reality: Benchmarks vs Intel (M1 vs Intel 10th/11th gen Core i5/i7)

Summary:
- Early, high-profile reviews (AnandTech) and community benchmark reports showed Apples M1 family delivered unusually strong single-thread performance and exceptional efficiency compared with contemporary Intel 10th/11th gen mobile CPUs (Geekbench and Cinebench single-core leads; extremely low idle power) (https://www.anandtech.com/Show/Index/16252?cPage=64&all=False&sort=0&page=1&slug=mac-mini-apple-m1-tested, 2020; https://www.anandtech.com/Show/Index/17024?cPage=50&all=False&sort=0&page=3&slug=apple-m1-max-performance-review, 2021).
- However, initial single-run Cinebench/Geekbench scores were sometimes amplified in social posts and do not reflect sustained throughput or power-limited performance; long-loop Cinebench runs and power/thermal traces are required to reveal throttling, especially for fanless MacBook Air designs versus actively cooled Intel laptops (https://www.techpowerup.com/274764/apple-m1-beats-intel-willow-cove-in-cinebench-r23-single-core-test?cp=4, 2020; https://forums.macrumors.com/threads/m1-macbook-air-30-minute-cinebench-r23-score.2277378/, 2020).

Key patterns/tensions to follow up in later rounds:
1) M1 dominance vs Intel in single-thread and lightweight workloads, leading to better perceived real-world responsiveness and higher performance-per-watt for bursts.
2) Sustained multi-core throughput depends heavily on device thermal design; fanless M1 MacBook Air may see throttling under long workloads vs cooled Intel machines and M1 Pro/Max variants.
3) Measurement methodology matters: package-level power counters (available on M1 Pro/Max via Apple telemetry) vs wall AC power (used by many reviews) yield different conclusions about chip-level efficiency.

Representative sources discovered this round:
- AnandTech, "The 2020 Mac Mini Unleashed: Putting Apple Silicon M1 To The Test" (https://www.anandtech.com/Show/Index/16252?cPage=64&all=False&sort=0&page=1&slug=mac-mini-apple-m1-tested, 2020)
- AnandTech, "Apple's M1 Pro, M1 Max SoCs Investigated: New Performance and Efficiency Heights" (https://www.anandtech.com/Show/Index/17024?cPage=50&all=False&sort=0&page=3&slug=apple-m1-max-performance-review, 2021)
- TechPowerUp, "Apple M1 Beats Intel 'Willow Cove' in Cinebench R23 Single Core" (https://www.techpowerup.com/274764/apple-m1-beats-intel-willow-cove-in-cinebench-r23-single-core-test?cp=4, 2020)
- MacRumors forum discussion about 30-minute Cinebench runs on M1 MacBook Air (https://forums.macrumors.com/threads/m1-macbook-air-30-minute-cinebench-r23-score.2277378/, 2020)

Next steps (reserve up to one more search this round):
- Target independent, model-specific benchmark sources that publish detailed sustained-power/time traces and real-world workloads (Notebookcheck, LaptopMag, Ars Technica, Puget Systems, SPEC reports, Blender/FFmpeg/ccs compile timings).
- Capture actual numbers: Cinebench R23 single- and multi-core scores for M1 MacBook Air/Pro and Intel Core i5/i7 10th/11th gen laptops; power draw (W) and performance-per-watt calculations; compile/video-encode timings.


## Round 2 Findings
Timestamp: 2025-11-13T18:57:02Z

I ran focused searches for Notebookcheck and benchmark-aggregation pages to find hard numbers (Geekbench 5, Cinebench R23 sustained loops, power draw, and real-world timings) comparing Apple M1 to Intel Core i7-1165G7 (Tiger Lake) and Core i5-1035G1 (Ice Lake).

Findings and tensions (what the searches produced):
- Notebookcheck’s M1 reviews (MacBook Air and Pro coverage) consistently emphasize the same pattern: the M1 SoC delivers exceptional single-thread/burst performance and very low idle power, but the fanless MacBook Air variant will throttle under prolonged multi-core load compared with actively cooled designs (M1 MacBook Pro or Intel laptops). Notebookcheck recommends looped Cinebench R23 runs to reveal sustained throughput and compares chassis cooling impact directly (https://www.notebookcheck.net/Apple-MacBook-Air-2020-M1-Entry-Review-Apple-M1-CPU-humbles-Intel-and-AMD.508057.0.html, 2020; https://www.notebookcheck.net/Apple-MacBook-Pro-14-2021-Laptop-Review-The-performance-of-the-M1-Max-is-limited.612296.0.html, 2021).
- My targeted queries in this round did not return a single consolidated table with all the specific numeric values requested (Geekbench 5 single/multi scores for M1 vs Core i7-1165G7 vs Core i5-1035G1; Cinebench R23 single-thread and sustained multi-core loop values; measured idle/load watts and performance-per-watt; HandBrake/FFmpeg, Xcode, and Photoshop export timings) from the inspected sources within the limited search budget. Notebookcheck and forum threads point to methodology (run loops, compare fanless vs active cooling) but the precise per-model numbers require pulling specific device reviews or benchmark pages (e.g., LaptopMag, Puget Systems, AnandTech device reviews, Geekbench Browser, or Notebookcheck device pages) which I have not yet fetched in this round (https://www.notebookcheck.net/i7-1165G7-vs-i5-1035G1_12118_11411.247596.0.html, 2023; https://cpu.userbenchmark.com/Compare/Intel-Core-i7-1165G7-vs-Intel-Core-i5-1035G1/m1195374vsm895407, n.d.; https://forums.macrumors.com/threads/m1-macbook-air-30-minute-cinebench-r23-score.2277378/, 2020).

Immediate takeaway for the seminar:
- The qualitative story is confirmed: M1 wins on burst single-thread performance and energy efficiency; sustained multi-core advantage depends on thermal design. However, I could not produce the requested hard numeric table in this round because the focused searches returned methodological guidance and device-specific narratives (Notebookcheck) rather than a single consolidated set of numbers for the three target CPUs. To deliver the exact Geekbench and Cinebench numbers, power draw (W), performance-per-watt, and real-world timings, I should fetch (1) individual device reviews that publish those exact metrics (Notebookcheck device pages, LaptopMag full reviews, AnandTech laptop reviews, Puget Systems creative app tests), and (2) the Geekbench Browser and Cinebench R23 published results pages for each CPU/device. Those are next-step searches.

Representative sources discovered this round:
- Notebookcheck, "Apple MacBook Air 2020 M1 Entry Review" (https://www.notebookcheck.net/Apple-MacBook-Air-2020-M1-Entry-Review-Apple-M1-CPU-humbles-Intel-and-AMD.508057.0.html, 2020)
- Notebookcheck, "Apple MacBook Pro 14 2021 Laptop Review" (https://www.notebookcheck.net/Apple-MacBook-Pro-14-2021-Laptop-Review-The-performance-of-the-M1-Max-is-limited.612296.0.html, 2021)
- Notebookcheck, "Intel Core i7-1165G7 vs Intel Core i5-1035G1" (https://www.notebookcheck.net/i7-1165G7-vs-i5-1035G1_12118_11411.247596.0.html, 2023)
- UserBenchmark, "Intel Core i7-1165G7 vs Intel Core i5-1035G1" (https://cpu.userbenchmark.com/Compare/Intel-Core-i7-1165G7-vs-Intel-Core-i5-1035G1/m1195374vsm895407, n.d.);
- MacRumors forum thread on 30-minute Cinebench R23 for M1 MacBook Air (https://forums.macrumors.com/threads/m1-macbook-air-30-minute-cinebench-r23-score.2277378/, 2020)

Next actions (if you want round 3):
- I will run 1-2 targeted searches (within the remaining allowed searches) to extract hard numbers from: Geekbench Browser (per-CPU/device scores), Notebookcheck device pages (detailed Cinebench R23 single/loop results, power/temperature logs), AnandTech and LaptopMag laptop reviews (power/efficiency traces), and Puget Systems creative app benchmark pages (Photoshop/Lightroom/DaVinci/encoding timings). Then I will append a numeric table with citations and simple performance-per-watt calculations.

Notes on methodology:
- For fairness, compare like-for-like chassis/power budgets where possible (e.g., ultralight Intel laptops with configured PL1/PL2 vs M1 MacBook Air/Pro). Prefer wall AC power measurements for whole-system comparisons and package-level telemetry where available for chip-level efficiency.


