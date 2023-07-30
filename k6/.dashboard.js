// helper for adding p(99) to existing chart
function addP99(chart) {
  chart.series = {
    ...chart.series,
    "http_req_duration_trend_p(99)": { label: "p(99)" },
  };
}

function addDroppedIterations(chart) {
  chart.series = {
    ...chart.series,
    dropped_iterations_counter_rate: { label: "dropped_iterations", scale: "1/s" },
  };
}

console.log(defaultConfig);

// add p(99) to overview panels request duration charts
addP99(defaultConfig.tab("overview_snapshot").chart("http_req_duration"));
addP99(defaultConfig.tab("overview_cumulative").chart("http_req_duration"));

// add p(99) to overview panels request duration charts
addDroppedIterations(defaultConfig.tab("overview_snapshot").chart("http_reqs"));
addDroppedIterations(
  defaultConfig.tab("overview_cumulative").chart("http_reqs")
);

export default defaultConfig;
