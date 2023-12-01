const res = await fetch("https://www.1823.gov.hk/common/ical/en.json");
const text = await res.text();
const json = JSON.parse(text.trim());
console.log(json);