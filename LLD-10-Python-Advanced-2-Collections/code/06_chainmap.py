"""ChainMap — layered dict lookups. First match wins."""
from collections import ChainMap


# --- Problem: merging config from multiple sources ---
# Default config → env config → user overrides
defaults = {"theme": "dark", "font_size": 14, "language": "en"}
env_config = {"font_size": 16, "debug": True}
user_prefs = {"theme": "light"}

# Without ChainMap: merge manually (overwrites, copies, messy)
merged = {**defaults, **env_config, **user_prefs}
print(f"Manual merge: {merged}")


# --- With ChainMap: layered lookup, no copying ---
config = ChainMap(user_prefs, env_config, defaults)
# Lookup order: user_prefs → env_config → defaults (first match wins)

print(f"\nChainMap lookup:")
print(f"  config['theme']     = '{config['theme']}'")      # user_prefs wins
print(f"  config['font_size'] = {config['font_size']}")     # env_config wins
print(f"  config['language']  = '{config['language']}'")    # defaults fallback
print(f"  config['debug']     = {config['debug']}")         # env_config


# --- Key insight: no data is copied ---
# Modifying the original dict is reflected in ChainMap
user_prefs["theme"] = "solarized"
print(f"\n  After user_prefs['theme'] = 'solarized':")
print(f"  config['theme'] = '{config['theme']}'")  # reflects change!


# --- .new_child() — add a layer on top ---
runtime = config.new_child({"debug": False, "verbose": True})
print(f"\n  new_child: debug={runtime['debug']}, verbose={runtime['verbose']}")
print(f"  Original config: debug={config['debug']}")  # unchanged


# --- Real-world: Django settings, CLI args ---
print("\n--- Use cases ---")
print("  • Config layering: defaults → env → user → CLI args")
print("  • Django settings: base.py → dev.py → local.py")
print("  • Template variable scopes: global → block → local")
print("  • Python's own scope resolution (local → enclosing → global → builtin)")
