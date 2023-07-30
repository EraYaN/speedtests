import {
  randomItem,
  tagWithCurrentStageIndex,
  randomIntBetween,
  randomString,
} from "https://jslib.k6.io/k6-utils/1.4.0/index.js";
import http from "k6/http";

import { SharedArray } from "k6/data";

const codes = new SharedArray("barcodes", function () {
  console.log("Loading barcodes...");
  // All heavy work (opening and processing big files for example) should be done inside here.
  // This way it will happen only once and the result will be shared between all VUs, saving time and memory.
  const f = JSON.parse(open("./barcodes.json"));
  return f; // f must be an array
});

http.setResponseCallback(http.expectedStatuses(200, 404));

export function barcodeLookup(url) {
  return function () {
    tagWithCurrentStageIndex();
    let barcode = "";
    if (randomIntBetween(0, 100) < 5) {
      // generate 404
      barcode = randomString(8);
    } else {
      // generate 200
      barcode = randomItem(codes);
    }
    const res = http.get(`${url}/barcode/lookup?barcode=${barcode}`, {
      tags: { name: "Lookup" },
    });
  };
}

export function barcodeTemplate(url) {
  return function () {
    tagWithCurrentStageIndex();
    let barcode = "";
    if (randomIntBetween(0, 100) < 5) {
      // generate 404
      barcode = randomString(8);
    } else {
      // generate 200
      barcode = randomItem(codes);
    }
    const res = http.get(`${url}/barcode/template?barcode=${barcode}`, {
      tags: { name: "Template" },
    });
  };
}

export function makeHandleSummary(name) {
  return function (data) {
    let fileName = `data/${name}-summary.json`;
    let obj = {};
    obj[fileName] = JSON.stringify(data);
    return obj;
  };
}
