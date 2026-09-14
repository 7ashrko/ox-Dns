
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pathlib import Path
import subprocess, re, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret")
BLOCK = Path("/etc/unbound/ps4-blocklist.conf")
UNBOUND_CONF = Path("/etc/unbound/unbound.conf")

def domains():
    if not BLOCK.exists(): return []
    out=[]
    for line in BLOCK.read_text(errors="ignore").splitlines():
        m=re.match(r'\s*local-zone:\s*"([^"]+)"\s+always_nxdomain', line)
        if m: out.append(m.group(1))
    return out

def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True, timeout=10)

@app.route("/")
def index():
    d=domains()
    active=run(["systemctl","is-active","unbound"]).stdout.strip()=="active"
    return render_template("index.html", domains=d, active=active)

@app.route("/domains", methods=["POST"])
def add_domain():
    d=request.form.get("domain","").strip().lower().rstrip(".")
    if not re.fullmatch(r"(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", d):
        flash("Invalid domain name.", "error"); return redirect(url_for("index"))
    current=domains()
    if d not in current:
        with BLOCK.open("a") as f: f.write(f'\nlocal-zone: "{d}" always_nxdomain\n')
        chk=run(["unbound-checkconf",str(UNBOUND_CONF)])
        if chk.returncode!=0:
            text=BLOCK.read_text()
            text=text.replace(f'\nlocal-zone: "{d}" always_nxdomain\n',"")
            BLOCK.write_text(text)
            flash("Configuration rejected by Unbound.", "error")
        else:
            run(["systemctl","reload","unbound"])
            flash(f"{d} blocked.", "ok")
    return redirect(url_for("index"))

@app.route("/domains/delete", methods=["POST"])
def delete_domain():
    d=request.form.get("domain","")
    text=BLOCK.read_text(errors="ignore")
    text=re.sub(rf'^\s*local-zone:\s*"{re.escape(d)}"\s+always_nxdomain\s*\n?', '', text, flags=re.M)
    BLOCK.write_text(text)
    run(["unbound-checkconf",str(UNBOUND_CONF)])
    run(["systemctl","reload","unbound"])
    flash(f"{d} removed.", "ok")
    return redirect(url_for("index"))

@app.route("/api/status")
def status():
    active=run(["systemctl","is-active","unbound"]).stdout.strip()
    return jsonify(unbound=active, blocked=len(domains()))

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080)
