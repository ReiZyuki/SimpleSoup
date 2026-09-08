from simplesoup import rz

url = "https://youtu.be/5Eqb_-j3FDA?si=HXDa99A05ABE106m"

expression = (
    "rz.(title:title;"
    "video[0]:video;"
    "creator:creator;"
    "time:duration;"
    "{" + url + "})"
)

result = rz.run(expression)

print("\n--- SimpleSoup Result ---")
print("Title:", result.get("title"))
print("Creator:", result.get("creator"))
print("Time:", result.get("duration"))
print("File:", result.get("video"))
