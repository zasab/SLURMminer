<template>
  <div v-if="error.length > 0" class="p-2 d-flex justify-content-center">
    <p style="color: crimson;">{{ error }}</p>
  </div>
  <div class="d-flex flex-row justify-content-center" style="justify-content:center; align-items: center;">
    <div style="width:95%">
      <div class="d-flex flex-row" style="justify-content:space-between;">
        <div class="row p-4" style="width:100%">
          <div class="card m-auto">
            <div class="card-body">
              <div id="jobsnumovertime"></div>
              <a @click="showJobsnumovertimeAnalysis()" class="link text-primary">More analysis</a>
              <p id="jobsnumovertimehiddenanalysis" style="display:none;">
                Analyzing the number of submitted jobs over time can provide valuable insights into the workload and
                resource utilization trends on a SLURM system. Here are a few key aspects that can be inferred from such a
                plot:
              <ul>
                <li>Workload Patterns: The plot can reveal patterns in job submission, such as daily or weekly
                  fluctuations. This information helps administrators and users understand the system's usage patterns and
                  plan resource allocations accordingly. For example, if there is a consistent surge in job submissions on
                  certain days or during specific times, additional resources can be allocated to handle the increased
                  demand.</li>
                <li>System Utilization: By observing the number of submitted jobs over time, you can assess the overall
                  system utilization. If the plot consistently shows high job submission rates, it indicates a high demand
                  for computing resources. Conversely, a low submission rate might suggest underutilization or an idle
                  system. This information can guide decisions regarding system configuration, capacity planning, and
                  optimization efforts.</li>
                <li>Workload Balancing: The plot can help identify imbalances in job distribution across time. For
                  instance, if certain time periods consistently have significantly more job submissions than others, it
                  might indicate a need to balance the workload to ensure fair resource allocation and reduce queuing
                  times
                  for users. Load balancing measures, such as job scheduling policies or adjustments to resource
                  allocation,
                  can be implemented based on these insights.</li>
                <li>Anomaly Detection: Unusual spikes or drops in the number of submitted jobs can indicate system issues,
                  user behavior changes, or unexpected events. Monitoring these anomalies can help administrators identify
                  and address potential problems. For example, a sudden drop in job submissions may indicate a
                  connectivity
                  issue, while a sharp spike might suggest a misconfiguration or a sudden increase in demand. Detecting
                  such
                  anomalies promptly allows for timely troubleshooting and system maintenance.</li>
                <li>User Behavior and Performance Evaluation: Analyzing the number of submitted jobs over time can provide
                  insights into user behavior and performance trends. It can help answer questions such as which users or
                  user groups are more active, which types of jobs are frequently submitted, or which users consistently
                  exceed resource limits. These insights can guide user support, resource allocation policies, and
                  optimization efforts.</li>

                <p style="margin-top:10px;color: red;">
                  To close the description, simply click on the <strong>More analysis</strong> link located above.
                </p>
              </ul>
              </p>
            </div>
          </div>
        </div>
      </div>
      <div class="d-flex flex-row" style="justify-content:space-between;">
        <div class="row p-4" style="width:100%">
          <div class="card m-auto">
            <div class="card-body">
              <div id="jobsnumperaccount"></div>
              <a @click="showJobsnumperaccountAnalysis()" class="link text-primary">More analysis</a>
              <p id="jobsnumperaccounthiddenanalysis" style="display:none;">Analyzing the number of submitted jobs per
                account on a SLURM system can provide several insights and
                facilitate various types of analysis. Here are a few examples:

              <ul>
                <li>Workload distribution: The plot showing the number of submitted jobs per account can provide an
                  overview of how the workload is distributed among different users or accounts. It helps identify which
                  users or groups are utilizing the system more heavily and which ones are submitting fewer jobs.</li>
                <li>Resource utilization: By analyzing the number of submitted jobs per account, you can gain insights
                  into the resource utilization patterns of different users. You can identify users who consistently
                  submit
                  a large number of jobs, indicating they require significant computational resources. Conversely, you may
                  notice users who submit very few jobs, suggesting they may have underutilized resources that could be
                  allocated to other users.</li>
                <li>User behavior: The plot can help identify the behavior of different users or groups. It may reveal
                  patterns such as users who consistently submit jobs during specific time periods, users who submit jobs
                  with varying frequency, or users who have irregular submission patterns. This information can be
                  valuable
                  for understanding user requirements, optimizing resource allocation, and identifying potential
                  bottlenecks
                  in the system.</li>
                <li>Fairness and policy enforcement: Monitoring the number of submitted jobs per account can help
                  ensure fairness in resource allocation. It enables system administrators to identify any accounts that
                  are
                  monopolizing resources or exceeding their allocated quotas. It can also assist in enforcing system
                  policies regarding job submission limits, ensuring that users adhere to the established guidelines.</li>
                <li>Capacity planning: By analyzing the historical trends of the number of submitted jobs per account,
                  you can estimate future resource demands and plan system capacity accordingly. This information can aid
                  in
                  determining if additional resources are needed, optimizing system configurations, and allocating
                  resources
                  effectively to meet the demands of different users or projects</li>
              </ul>

              <p style="margin-top:10px;color: red;">
                To close the description, simply click on the <strong>More analysis</strong> link located above.
              </p>
              </p>
            </div>
          </div>
        </div>
      </div>
      <div class="d-flex flex-row" style="justify-content:space-between;">
        <div class="row p-4" style="width:100%">
          <div class="card m-auto">
            <div class="card-body">
              <div id="jobsnumcpus"></div>
              <a @click="showJobsnumcpusAnalysis()" class="link text-primary">More analysis</a>
              <p id="jobsnumcpushiddenanalysis" style="display:none;">Analyzing the number of submitted jobs per
                requested CPUs plot can provide valuable insights into the workload distribution and resource utilization
                on the SLURM system. This type of analysis helps you understand how many jobs are being submitted for
                various CPU requirements and can highlight patterns and trends in job submissions.

                Here are some potential insights you can gain from this analysis:

              <ul>
                <li>Workload distribution: The plot can give you an overview of the distribution of job submissions across
                  different CPU requirements. You can observe which CPU requests are the most common and whether there are
                  any dominant patterns or clusters.</li>
                <li>Resource utilization: By examining the number of jobs submitted per requested CPUs, you can assess how
                  effectively the system's resources are being utilized. It can help identify whether certain CPU
                  configurations are overused or underutilized, allowing you to optimize resource allocation.</li>
                <li>Job scheduling efficiency: The plot can indicate whether there are any bottlenecks or imbalances in
                  job scheduling. For example, if you notice a high number of jobs requesting a specific number of CPUs
                  but limited availability for that configuration, it suggests a potential issue in job scheduling and
                  resource allocation.</li>
                <li>Scaling behavior: Analyzing the number of submitted jobs per requested CPUs plot over time can reveal
                  scaling behavior. You can identify if there are any fluctuations or growth patterns in the distribution
                  of job submissions, which can help with capacity planning and scaling decisions.</li>
                <li>User behavior and job requirements: This analysis can also provide insights into user behavior and job
                  requirements. You may observe that certain users consistently request specific CPU configurations or
                  notice trends in job submissions based on their characteristics (e.g., research areas, job types).</li>
              </ul>
              <p style="margin-top:10px;color: red;">
                To close the description, simply click on the <strong>More analysis</strong> link located above.
              </p>
              </p>
            </div>
          </div>
        </div>
      </div>
      <div class="d-flex flex-row" style="justify-content:space-between;">
        <div class="row p-4" style="width:100%">
          <div class="card m-auto">
            <div class="card-body">
              <div id="jobsStates"></div>
              <p>This plot provides same insights as "Number of submitted jobs over time" plot.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapActions, mapWritableState } from "pinia";
import { slurmLogQueries } from "../../stores/APIs";
export default {
  name: "BIanalysis",
  methods: {
    sleep(time) {
      return new Promise((resolve) => setTimeout(resolve, time));
    },
    download(url) {
      window.location.href = url;
    },
    set_x_axis(x) {
      this.x_axis = x;
    },
    set_y_axis(y) {
      this.y_axis = y;
    },

    showJobsnumovertimeAnalysis() {
      var text = document.getElementById("jobsnumovertimehiddenanalysis");
      if (text.style.display == "none") {
        text.style.display = "block";
      } else {
        text.style.display = "none";
      }
    },

    showJobsnumperaccountAnalysis() {
      var text = document.getElementById("jobsnumperaccounthiddenanalysis");
      if (text.style.display == "none") {
        text.style.display = "block";
      } else {
        text.style.display = "none";
      }
    },

    showJobsnumcpusAnalysis() {
      var text = document.getElementById("jobsnumcpushiddenanalysis");
      if (text.style.display == "none") {
        text.style.display = "block";
      } else {
        text.style.display = "none";
      }
    },

    async get_scatter_plot() {
      try {
        this.error = ""
        this.distribution_model = ""
        this.scatter_model = ""
        this.getScatterPlotData({
          "x_axis": this.x_axis,
          "y_axis": this.y_axis
        });
      } catch (error) {
        console.log("error: ", error)
      }
    },
    ...mapActions(slurmLogQueries, ["getScatterPlotData"]),

    async get_job_distribution_plot() {
      try {
        this.error = ""
        this.scatter_model = ""
        this.distribution_model = ""
        this.getNumberOfSubmittedJobsOverTime()
        while (this.slurm_log_info.length == 0) {
          await this.sleep(1);
        }
        var slurm_log_info = JSON.parse(this.slurm_log_info)
        var plot_dimensions1 = {
          x: slurm_log_info["TIMESTAMP"],
          y: slurm_log_info["JOBCOUNT"],
          type: 'bar'
        };
        var plot_data = [plot_dimensions1];
        var layout = {
          title: 'Number of Submitted Jobs over Time',
          showlegend: false,
          fixedrange: false,
          xaxis: {
            title: "time",
            // type: 'linear',
            // showgrid: true,
            // autorange: true,
          },
          yaxis: {
            title: "submited jobs count",
            type: 'linear',
          },
        };
        Plotly.plot('jobsnumovertime', plot_data, layout, { scrollZoom: true });

        while (this.CPUS_JOBCOUNT.length == 0) {
          await this.sleep(1);
        }
        var CPUS_JOBCOUNT = JSON.parse(this.CPUS_JOBCOUNT)
        var plot_dimensions2 = {
          x: CPUS_JOBCOUNT["CPUS_JOBCOUNT"],
          y: CPUS_JOBCOUNT["CPUS"],
          type: 'bar',
          orientation: 'h'
        };
        var plot_data2 = [plot_dimensions2];
        var layout2 = {
          title: '#Jobs and Requested CPUs',
          showlegend: false,
          fixedrange: false,
          xaxis: {
            title: "number of jobs",
            type: 'linear',
          },
          yaxis: {
            title: "number of requested CPUs",
          },
        };
        Plotly.plot('jobsnumcpus', plot_data2, layout2, { scrollZoom: true });


        while (this.R_PD_TIME.length == 0) {
          await this.sleep(1);
        }
        var R_PD_TIME = JSON.parse(this.R_PD_TIME)
        var plot_dimensions3 = {
          x: R_PD_TIME["times"],
          y: R_PD_TIME["Rnums"],
          name: '#running',
          type: 'bar',
          orientation: 'v'
        };
        var plot_dimensions4 = {
          x: R_PD_TIME["times"],
          y: R_PD_TIME["PDnums"],
          name: '#pending',
          type: 'bar',
          orientation: 'v'
        };
        var plot_data3 = [plot_dimensions3, plot_dimensions4];
        var layout3 = {
          title: '#of Running and Pending Jobs over Time',
          showlegend: true,
          fixedrange: false,
          xaxis: {
            title: "time",
          },
          yaxis: {
            title: "number of running & pending jobs ",
            type: 'linear',
          },
        };
        Plotly.plot('jobsStates', plot_data3, layout3, { scrollZoom: true });


      } catch (error) {
        console.log("error: ", error)
      }
    },
    ...mapActions(slurmLogQueries, ["getNumberOfSubmittedJobsOverTime"]),

    async get_job_distribution_per_account_plot() {
      try {
        this.error = ""
        this.scatter_model = ""
        this.distribution_model = ""
        this.getNumberOfSubmittedJobsPerAccount()
        while (this.jobs_per_account.length == 0) {
          await this.sleep(1);
        }
        var jobs_per_account = JSON.parse(this.jobs_per_account)

        var plot_dimensions1 = {
          x: jobs_per_account["JOBCOUNT"],
          y: jobs_per_account["ACCOUNTS"],
          type: 'bar',
          orientation: 'h'
        };
        var plot_data = [plot_dimensions1];
        var layout = {
          title: 'Number of Submitted Jobs Per Account',
          showlegend: false,
          fixedrange: false,
          xaxis: {
            title: "number of submited jobs",
            type: 'linear',
          }
        };

        Plotly.plot('jobsnumperaccount', plot_data, layout, { scrollZoom: true });


      } catch (error) {
        console.log("error: ", error)
      }
    },
    ...mapActions(slurmLogQueries, ["getNumberOfSubmittedJobsPerAccount"]),

    async get_dotted_chart_jobid_duration_label() {
      try {
        this.error = ""
        this.scatter_model = ""
        this.distribution_model = ""
        this.getDottedJobidDurationLabel()
        while (this.time_jobs_state.length == 0) {
          await this.sleep(1);
        }
        var time_jobs_state = JSON.parse(this.time_jobs_state)
        var trace1 = {
          x: time_jobs_state['START'],
          y: time_jobs_state['JOBID_view'],
          mode: 'markers',
          type: 'scatter',
          name: time_jobs_state['DURATION_LABEL'],
          marker: {
            color: time_jobs_state['DURATION_LABEL']
          }
        };

        var data = [trace1];
        var layout = {
          title: 'JobID over Submitted time, colored by duration',
          showlegend: false,
          fixedrange: false,
          xaxis: {
            title: "time",
          }
        };
        Plotly.plot('jobsovertimedurationcolored', data, layout, { scrollZoom: true });

      } catch (error) {
        console.log("error: ", error)
      }
    },
    ...mapActions(slurmLogQueries, ["getDottedJobidDurationLabel"]),

  },
  computed: {
    ...mapWritableState(slurmLogQueries, [
      "slurm_log_content",
      "scatter_model",
      "error",
      "distribution_model",
      "slurm_log_info",
      "jobs_per_account",
      "time_jobs_state",
      'CPUS_JOBCOUNT',
      "R_PD_TIME",
      "distribution_loading"
    ]),
  },
  beforeMount() {
    this.error = ""
  },
  mounted() {
    this.get_job_distribution_plot();
    this.get_job_distribution_per_account_plot();
    this.get_dotted_chart_jobid_duration_label();
  },
};
</script>