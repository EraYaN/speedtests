const vus = 100;
const maxVUs = 2000;

const stopTime = "10s";

// Make the curve
const ramp_duration = 20;
const soak_duration = 10;
const step_duration = ramp_duration + soak_duration;
const total_duration = 300;

const start_load = 25;
const max_load = 5000;
const total_steps = Math.floor(total_duration / step_duration);
const factor = 3;

function getLoadForStep(x) {
  return Math.round(
    start_load + Math.pow(x / total_steps, factor) * (max_load - start_load)
  );
}

let stages = [];
let i = 0;
for (let step = 1; step <= total_steps; step++) {
  stages[i++] = { target: getLoadForStep(step), duration: `${ramp_duration}s` };
  stages[i++] = { target: getLoadForStep(step), duration: `${soak_duration}s` };
}
// Extra soak
stages[i++] = {
  target: getLoadForStep(total_steps),
  duration: `${soak_duration}s`,
};

export function loadOptions() {
  let defaults = {
    root_domain: "localhost",
  };

  try {
    let fileOptions = JSON.parse(open(".speedtest_options.json"));
    Object.assign(defaults, fileOptions);
  } catch (error) {} // File not found

  return defaults;
}

export const options = {
  discardResponseBodies: true,

  scenarios: {
    scans: {
      executor: "ramping-arrival-rate",
      startRate: 0,
      timeUnit: "1s",
      preAllocatedVUs: vus,
      maxVUs: maxVUs,
      gracefulStop: stopTime,
      stages: stages,
    },
  },

  thresholds: {
    // Some dummy thresholds that are always going to pass.
    "http_reqs{status:200}": ["count>=0"],
    "http_reqs{status:400}": ["count>=0"],
    "http_reqs{status:401}": ["count>=0"],
    "http_reqs{status:402}": ["count>=0"],
    "http_reqs{status:403}": ["count>=0"],
    "http_reqs{status:404}": ["count>=0"],
    "http_reqs{status:500}": ["count>=0"],
    "http_reqs{status:501}": ["count>=0"],
    "http_reqs{status:502}": ["count>=0"],
    "http_reqs{status:503}": ["count>=0"],
    "http_reqs{status:504}": ["count>=0"],
    http_req_failed: [
      {
        threshold: "rate < 500", // string
        abortOnFail: true, // boolean
        delayAbortEval: "0s", // string
      },
    ],
    dropped_iterations: [
      {
        threshold: "rate < 500", // string
        abortOnFail: true, // boolean
        delayAbortEval: "0s", // string
      },
    ],
    "http_req_duration{status:200}": [
      {
        threshold: "p(95) < 1000", // string
        abortOnFail: true, // boolean
        delayAbortEval: "10s", // string
      },
    ],
    "http_req_duration{status:404}": [
      {
        threshold: "p(95) < 1000", // string
        abortOnFail: true, // boolean
        delayAbortEval: "10s", // string
      },
    ],
  },
};
