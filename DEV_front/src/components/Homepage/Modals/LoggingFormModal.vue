<template>
  <div>
    <div class="modal fade" id="StartLoggingForm" aria-hidden="true" aria-labelledby="Logging" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-md">
        <div class="modal-content">
          <div class="modal-header">
            <h6 class="modal-title">
              <div class="d-flex">
                <span class="fw-bold text-primary pt-3 px-2">
                  <h5 class="text-primary">SLURM Logging</h5>
                </span>
              </div>
            </h6>
          </div>
          <div class="modal-body">
            <div class="container">
              <div class="row text-start">
                <div class="col-sm-12 col-md-12 col-lg-12 col-xl-12">
                  <div class="mb-3">
                    <label for="username" class="py-2 fw-bold form-label-custom">user name</label>
                    <div class="form-inputs">
                      <i class="bi bi-person"></i>
                      <input type="text" placeholder="" v-model="username" />
                    </div>
                  </div>
                </div>
                <div class="col-sm-12 col-md-12 col-lg-12 col-xl-12">
                  <div class="mb-3">
                    <label for="serverhost" class="py-2 fw-bold form-label-custom">Server Host</label>
                    <div class="form-inputs">
                      <i class="bi bi-person"></i>
                      <input type="text" placeholder="" v-model="serverhost" />
                    </div>
                  </div>
                </div>
                <div class="col-sm-12 col-md-12 col-lg-12 col-xl-12">
                  <div class="mb-3">
                    <label for="password" class="py-2 fw-bold form-label-custom">password</label>
                    <div class="form-inputs">
                      <i class="bi bi-key"></i>
                      <div class="input-icon">
                        <i class="bi" :class="showpassword ? 'bi-eye' : 'bi-eye-slash'"
                          @click="showpassword = !showpassword" style="cursor: pointer"></i>
                      </div>
                      <input :type="showpassword ? 'text' : 'password'" placeholder="" v-model="password" />
                    </div>
                  </div>
                </div>
                <div v-if="error.length == 0" class="d-flex justify-content-left flex-column">
                  <hr />
                  <p class="h4">Log description</p>
                  <p class="text-info">Number of unique accounts: <strong class="text-dark">{{ accounts }}</strong></p>
                  <p class="text-info">Number of unique job IDs: <strong class="text-dark">{{ job_id_numbers }}</strong></p>
                  <p class="text-info">From: <strong class="text-dark">{{ min_time }}</strong></p>
                  <p class="text-info">To: <strong class="text-dark">{{ max_time }}</strong></p>
                </div>
                <div v-if="error.length > 0" class="p-4 d-flex justify-content-center">
                  <p style="color: crimson;">{{ error }}</p>
                </div>
                <div class="d-flex pt-2 border-top" style="width:100%; justify-content: space-between;">
                  <button class="btn btn-warning" type="submit" @click="restart_logging">
                    Restart Logging
                  </button>
                  <button class="btn btn-success" type="submit" @click="submit">
                    Start Logging
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapActions } from "pinia";
import { startLoggingQuery } from "../../../stores/APIs";
import { mapWritableState } from "pinia";
export default {
  name: "LoggingForm",
  data() {
    return {
      showpassword: false,
      timer: null,
    };
  },
  methods: {
    submit() {
      try {
        this.getData(this.login);
      } catch (error) {
        console.log("error-: ", error)
      }
    },
    ...mapActions(startLoggingQuery, ["getData"]),

    restart_logging() {
      try {
        this.restart_logging();
      } catch (error) {
        console.log("error-:", error);
      }
    },
    ...mapActions(startLoggingQuery, ["restart_logging"]),
  },
  computed: {
    ...mapWritableState(startLoggingQuery, [
      "username",
      "password",
      "serverhost",
      "totalCount",
      "error",
      "accounts",
      "job_id_numbers",
      "min_time",
      "max_time"
    ]),
  },
  beforeMount() {
    this.error = ""
  },
};
</script>
