import subprocess
import os

git = r"C:\Program Files\Git\cmd\git.exe"
print("Staging files...")
r1 = subprocess.run([git, "add", "."])
print("Add result:", r1.returncode)

print("Committing...")
r2 = subprocess.run([
    git, "commit", "-m",
    "Implement retro-pixel RPG Log In and Create Account screens with authentication",
    "--author=afiabyte <278535610+afiabyte@users.noreply.github.com>"
])
print("Commit result:", r2.returncode)

print("Pushing...")
r3 = subprocess.run([git, "push", "origin", "main"])
print("Push result:", r3.returncode)
