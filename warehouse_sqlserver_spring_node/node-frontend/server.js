const http = require("http");
const fs = require("fs");
const path = require("path");

const port = Number(process.env.FRONTEND_PORT || 3000);
const root = path.join(__dirname, "public");

const types = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8"
};

http.createServer((req, res) => {
  const urlPath = req.url === "/" ? "/index.html" : req.url.split("?")[0];
  const file = path.join(root, path.normalize(urlPath));
  if (!file.startsWith(root)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }
  fs.readFile(file, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    res.writeHead(200, { "Content-Type": types[path.extname(file)] || "text/plain; charset=utf-8" });
    res.end(data);
  });
}).listen(port, () => {
  console.log(`Frontend: http://127.0.0.1:${port}`);
});
