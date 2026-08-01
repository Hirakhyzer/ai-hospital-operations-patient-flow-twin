% Plot synthetic hospital operations metrics exported by the Python pipeline.
resultsDir = fullfile('outputs', 'results');

capacity = readtable(fullfile(resultsDir, 'synthetic_capacity_audit.csv'));
figure;
bar(categorical(capacity.unit_id), capacity.capacity_pressure_score);
title('Synthetic Capacity Pressure');
xlabel('Unit');
ylabel('Pressure Score');

staffing = readtable(fullfile(resultsDir, 'synthetic_staffing_audit.csv'));
figure;
bar(categorical(staffing.unit_id), staffing.staff_workload_score);
title('Synthetic Staff Workload');
xlabel('Unit');
ylabel('Workload Score');
