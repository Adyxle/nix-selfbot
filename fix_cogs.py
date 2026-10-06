import os, re

for f in os.listdir("cogs"):
    if f.endswith(".py"):
        p = os.path.join("cogs", f)
        s = open(p, encoding="utf-8").read()
        new = re.sub(r"^def setup\(", "async def setup(", s, flags=re.M)
        new = re.sub(r"^(\s+)(\w+)\.add_cog\(", r"\1await \2.add_cog(", new, flags=re.M)
        if new != s:
            open(p, "w", encoding="utf-8").write(new)
            print("fixed", f)
print("done")