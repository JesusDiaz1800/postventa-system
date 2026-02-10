
import sys
import os

# Ensure we can find the package
# sys.path.append(os.getcwd()) 

try:
    from notebooklm_mcp.auth import load_cached_tokens
    from notebooklm_mcp.api_client import NotebookLMClient
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def verify():
    print("Loading cached tokens...")
    tokens = load_cached_tokens()
    if not tokens:
        print("No tokens found! Authentication failed.")
        return

    print(f"Tokens loaded. CSRF present: {bool(tokens.csrf_token)}")
    
    client = NotebookLMClient(
        cookies=tokens.cookies,
        csrf_token=tokens.csrf_token,
        session_id=tokens.session_id
    )
    
    print("Attempting to list notebooks...")
    try:
        notebooks = client.list_notebooks()
        print(f"\nSUCCESS! Found {len(notebooks)} notebooks:")
        for nb in notebooks:
            print(f"- {nb.title} (ID: {nb.id})")
            
    except Exception as e:
        print(f"\nERROR: Failed to list notebooks. {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
