import {
    barcodeLookup,
    barcodeTemplate,
    makeHandleSummary,
  } from "./shared/tests.js";
  import {
    options as globOptions,
    loadOptions,
  } from "./shared/global-options.js";
  
  export const options = globOptions;
  
  const LANG = "localhost";
  const ENDPOINT = __ENV.ENDPOINT ? __ENV.ENDPOINT : "lookup";
  
  const OPTS = loadOptions();
  
  export const handleSummary = makeHandleSummary(LANG);
  
  let testFunction = barcodeLookup(`http://localhost:3000`); // By default hit the lookup endpoint
  
  if (ENDPOINT === "template") {
    testFunction = barcodeTemplate(`http://localhost:3000`);
  }
  
  export default testFunction;