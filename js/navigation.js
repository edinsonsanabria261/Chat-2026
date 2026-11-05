import "./main.js";

const tabs = ["hub", "crud", "telemetry"];
for (const name of tabs) {
  const button = document.getElementById(`tab-${name}`);
  button?.addEventListener("click", () => {
    for (const panelName of tabs) {
      const selected = panelName === name;
      document.getElementById(`panel-${panelName}`).hidden = !selected;
      document.getElementById(`tab-${panelName}`).setAttribute("aria-selected", String(selected));
    }
  });
}
