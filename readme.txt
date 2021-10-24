The folders are explained as follows.

1. adaptive_im: codes for adaptive/online influence influence maximization.
2. non_adaptive_im: codes for non-adaptive/offline influence influence maximization.
3. compilation: codes for averaging and plotting.
4. exp_influences: codes for calculating true influences.
5. stoch_dom: codes for verifying the FSD assumption.

Flowchart to run:

1. Run main_multi_run inside the adaptive_im folder. Results are generated inside a folder named results_<name_id> with the adaptive_im folder.

2. OPTIONALLY run main_offline inside the non_adaptive_im folder. Time taking for large networks. Usually not needed. Results are generated inside a folder named results_<name_id> with the non_adaptive_im folder. For each algorithm, a single file is generated for all integer budgets up-to the maximum budget.

Not that the main_offline script runs only nested non-adaptive algorithms. For optimal solution, run optimal_im, USUALLY VERY TIME TAKING.

3. Run main1_avg and then main2_plot inside the compilation folder. Results are generated inside a folder named results_<name_id> with the compilation folder. Note: The format for inputs in the main file(s) in the compilation folder is STRING entries contrary to the main files in other folders. 


Runnable methods: dart, cmab, ucbgr