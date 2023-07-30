import { barcodeLookup, makeHandleSummary } from "./shared/tests.js";
import {
  options as globOptions,
  loadOptions,
} from "./shared/global-options.js";

export const options = globOptions;

const LANG = __ENV.LANG ? __ENV.LANG : test.abort("Language name not given...");

const OPTS = loadOptions();

export const handleSummary = makeHandleSummary(LANG);

export default barcodeLookup(`https://${LANG}.${OPTS["root_domain"]}`);
