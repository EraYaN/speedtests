import { barcodeLookup, makeHandleSummary } from "./shared/tests.js";
import { options as globOptions } from "./shared/global-options.js";

export const options = globOptions;

const NAME = "localhost";

export const handleSummary = makeHandleSummary(NAME);

export default barcodeLookup(`http://localhost:3000`);
