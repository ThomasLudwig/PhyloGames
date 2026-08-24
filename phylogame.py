import json
import os
import secrets
import shutil
import string
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from python import startgame, evaluator


##Global const
HOST = "0.0.0.0" #Server address
PORT = 8000 #Server port
POOL = string.ascii_letters + string.digits #sessions character pool
SLEN = 4 #sessions name length
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR  = os.path.abspath(os.path.join(BASE_DIR, "sessions"))

## HTTPRequestHandler
class Handler(SimpleHTTPRequestHandler):
  ##Handle POST
  def do_POST(self):
    if self.path == "/api/session":
      self.create_session()
    if self.path == "/api/evaluate":
      self.evaluate()
    if self.path == "/api/solve":
      self.solve()
    if self.path == "/api/showAll" :
      self.showAll()
    else:
      self.send_error(404)

  ##Handle DELETE
  def do_DELETE(self):
    parsed = urlparse(self.path)
    if parsed.path.startswith("/api/session/"):
      session_id = parsed.path.split("/")[-1]
      self.delete_session(session_id)
    else:
      self.send_error(404)

  ##Create new session
  def create_session(self):
    session_id = self.generate_session_id()
    session_dir = os.path.join(TMP_DIR, session_id)
    #Create tmpdir
    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(session_dir)
    # Read parameters sent by JavaScript
    length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(length)
    parameters = json.loads(body)
    # Generate Game(session) files
    startgame.prepare(session_id, session_dir, parameters)
    # Send session ID back to JavaScript
    response = json.dumps({"sessionId": session_id}).encode()
    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", len(response))
    self.end_headers()
    self.wfile.write(response)

  def evaluate(self):
    # Read parameters sent by JavaScript
    length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(length)
    parameters = json.loads(body)
    session = parameters["session"]
    query =  parameters["query"]

    print(f"Session {session}")
    print(f"Query {query}")
    # Compute result
    result = evaluator.evaluate(session, query)
    print(f"Booleans {result}")

    # Send result back to JavaScript
    response = json.dumps({"result": result}).encode()
    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", len(response))
    self.end_headers()
    self.wfile.write(response)

  def solve(self):
    # Read parameters sent by JavaScript
    length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(length)
    parameters = json.loads(body)
    session = parameters["session"]

    print(f"Session {session}")
    # Compute result
    result = evaluator.solve(session)
    print(f"Sorted {result}")

    # Send result back to JavaScript
    response = json.dumps({"result": result}).encode()
    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", len(response))
    self.end_headers()
    self.wfile.write(response)

  def showAll(self):
    # Read parameters sent by JavaScript
        result = startgame.listAllSpecies()
    
        # Send result back to JavaScript
        response = json.dumps({"result": result}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)

  ##Deletes session
  def delete_session(self, session_id):
    # Basic protection against paths such as ../
    if len(session_id) != SLEN or not all(c in POOL for c in session_id):
      self.send_error(400, "Invalid session ID")
      return
    session_dir = os.path.join(TMP_DIR, session_id)
    if os.path.isdir(session_dir):
      shutil.rmtree(session_dir)
    self.send_response(204)
    self.end_headers()

  ##Generates a new sessions ID
  def generate_session_id(self):
    while True:
      session_id = "".join(secrets.choice(POOL) for _ in range(SLEN))
      session_dir = os.path.join(TMP_DIR, session_id)
      if not os.path.exists(session_dir):
        return session_id

#########################
#########################
#########################

# Main code
server = HTTPServer((HOST, PORT), Handler)
print(f"Server running at http://{HOST}:{PORT}")
server.serve_forever()