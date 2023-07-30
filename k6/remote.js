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

const LANG = __ENV.LANG ? __ENV.LANG : test.abort("Language name not given...");
const ENDPOINT = __ENV.ENDPOINT ? __ENV.ENDPOINT : "lookup";

const OPTS = loadOptions();

export const handleSummary = makeHandleSummary(`${LANG}-${ENDPOINT}`);

let testFunction = barcodeLookup(`https://${LANG}.${OPTS["root_domain"]}`); // By default hit the lookup endpoint

if (ENDPOINT === "template") {
  testFunction = barcodeTemplate(`https://${LANG}.${OPTS["root_domain"]}`);
}

export default testFunction;
