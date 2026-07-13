import re
import httpx
import tomllib
from typing import List, Dict
from github import Github

class GitEngine:
    """
    Engine responsible for scanning GitHub repositories for exposed API keys.
    """
    # Simple mock regex for API key detection (e.g., 'sk_live_...', 'pk_live_...')
    SECRET_PATTERNS = {
        "Stripe": r"(sk_live_[0-9a-zA-Z]{24})",
        "AWS": r"(AKIA[0-9A-Z]{16})",
        "Generic Token": r"(?i)bearer\s+([a-zA-Z0-9\-\._~+/]+=*)"
    }
    
    _gitleaks_patterns = None

    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self._load_gitleaks_patterns()

    @classmethod
    def _load_gitleaks_patterns(cls):
        if cls._gitleaks_patterns is not None:
            return
        
        try:
            # Fetch the robust regex patterns from gitleaks
            response = httpx.get("https://raw.githubusercontent.com/gitleaks/gitleaks/master/config/gitleaks.toml", timeout=10.0)
            response.raise_for_status()
            config = tomllib.loads(response.text)
            
            patterns = {}
            for rule in config.get("rules", []):
                provider = rule.get("id")
                regex = rule.get("regex")
                if provider and regex:
                    try:
                        # Test if the regex is valid in Python's re engine
                        re.compile(regex)
                        patterns[provider] = regex
                    except re.error:
                        pass
                        
            if patterns:
                cls._gitleaks_patterns = patterns
            else:
                cls._gitleaks_patterns = cls.SECRET_PATTERNS
        except Exception as e:
            print(f"Error loading gitleaks patterns: {e}")
            cls._gitleaks_patterns = cls.SECRET_PATTERNS

    def scan_repository(self, repo_name: str) -> List[Dict]:
        """
        Scans a repository for exposed secrets.
        """
        discovered_keys = []
        try:
            repo = self.github.get_repo(repo_name)
            contents = repo.get_contents("")
            
            # Simple breadth-first search through repo contents
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    # Only scan text-like files for simplicity
                    if file_content.name.endswith(('.js', '.ts', '.py', '.json', '.env', '.txt')):
                        try:
                            text = file_content.decoded_content.decode('utf-8')
                            patterns_to_use = self._gitleaks_patterns if self._gitleaks_patterns else self.SECRET_PATTERNS
                            for provider, pattern in patterns_to_use.items():
                                try:
                                    matches = re.finditer(pattern, text)
                                    for match in matches:
                                        matched_text = match.group(1) if match.groups() and match.group(1) else match.group(0)
                                        
                                        if len(matched_text) > 10:
                                            hashed_key = matched_text[:5] + "..." + matched_text[-5:]
                                        else:
                                            hashed_key = matched_text[:2] + "..."
                                            
                                        discovered_keys.append({
                                            "provider": provider,
                                            "key_hash": hashed_key,
                                            "source": file_content.path,
                                            "link": file_content.html_url,
                                            "repository": repo_name,
                                            "risk_level": "high"
                                        })
                                except Exception:
                                    pass # Skip on regex matching errors
                        except Exception:
                            pass # Skip non-decodable files
        except Exception as e:
            # Log the error (can be caught by the worker)
            print(f"Error scanning {repo_name}: {e}")
            
        return discovered_keys
