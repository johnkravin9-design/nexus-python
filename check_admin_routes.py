from app import app

print("Registered routes:")
for rule in app.url_map.iter_rules():
    if 'admin' in rule.rule:
        print(f"  {rule.rule} -> {rule.endpoint}")
