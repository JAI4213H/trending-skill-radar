import json, sys, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from connectors import CollectionError, fetch_json

class Response:
    def __enter__(self): return self
    def __exit__(self, *args): return None
    def read(self): return json.dumps({"ok": True}).encode()

class ConnectorTests(unittest.TestCase):
    @patch("connectors.urlopen", return_value=Response())
    def test_documented_json_fetch(self, opened):
        self.assertEqual(fetch_json("https://example.test/api"), {"ok": True})
        self.assertTrue(opened.called)

if __name__ == "__main__": unittest.main()
