app.get("/health", (_req, res) => {
  res.json({ ok: true, status: "healthy", uptime: process.uptime() });
});

app.use("/css", express.static(path.join(root, "css")));
app.use("/js", express.static(path.join(root, "js")));
app.get("/", (_req, res) => res.sendFile(path.join(root, "index.html")));
