import json

# Load Harper's personality files
with open("harper/harper_core.json") as f:
    core = json.load(f)
with open("harper/harper_barelySane.json") as f:
    heather = json.load(f)
with open("harper/harper_chuckles.json") as f:
    chuck = json.load(f)

print("🦋 Harper is online and listening...")
print(f"Core empathy level: {core['empathy']}")
print(f"Heather profile loaded: {heather['name']}")
print(f"Chuck profile loaded: {chuck['name']}")

