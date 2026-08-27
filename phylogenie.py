import json
import os
import secrets
import shutil
import string
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

from python import evaluator, startgame

##Global const
HOST = "0.0.0.0" #Server address
PORT = 8000 #Server port
POOL = string.ascii_letters + string.digits #sessions character pool
SLEN = 4 #sessions name length
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR  = os.path.abspath(os.path.join(BASE_DIR, "sessions"))
shutil.rmtree(TMP_DIR, ignore_errors=True)

class Handler(SimpleHTTPRequestHandler):
  """
  HTTPRequestHandler
  """
  def do_POST(self):
    """
    Handles POST requests
    """  
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

  def create_session(self):
    """
    Creates a new session
    """
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
    """
    Evaluates the user's answers
    """
    # Read parameters sent by JavaScript
    length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(length)
    parameters = json.loads(body)
    session = parameters["session"]
    query =  parameters["query"]

    # Compute result
    result = evaluator.evaluate(session, query)
    
    # Send result back to JavaScript
    response = json.dumps({"result": result}).encode()
    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", len(response))
    self.end_headers()
    self.wfile.write(response)

  def solve(self):
    """
    Solves the tree
    """
    # Read parameters sent by JavaScript
    length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(length)
    parameters = json.loads(body)
    session = parameters["session"]

    # Compute result
    result = evaluator.solve(session)

    # Send result back to JavaScript
    response = json.dumps({"result": result}).encode()
    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", len(response))
    self.end_headers()
    self.wfile.write(response)

  def showAll(self):
    """
    Hidden options to display all the available species
    """
    result = startgame.listAllSpecies()
    # Send result back to JavaScript
    response = json.dumps({"result": result}).encode()
    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", len(response))
    self.end_headers()
    self.wfile.write(response)

  def generate_session_id(self):
    """
    Generates a new sessions ID
    """
    while True:
      session_id = "".join(secrets.choice(POOL) for _ in range(SLEN))
      session_dir = os.path.join(TMP_DIR, session_id)
      if not os.path.exists(session_dir):
        return session_id

######################
#######  Main  #######
######################

print("Please wait...")
server = HTTPServer((HOST, PORT), Handler)
print(f"Server running at http://{HOST}:{PORT}")
print(f"Open http://localhost:{PORT} in a browser")
server.serve_forever()