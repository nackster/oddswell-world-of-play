"""Run bounded, isolated character checks against an existing Windows package."""
import argparse
import json
import subprocess
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--package", type=Path, required=True)
parser.add_argument("--evidence", type=Path, required=True)
args = parser.parse_args()
exe = args.package.resolve() / "OddsWell/Binaries/Win64/OddsWell.exe"
assert exe.is_file()
root = args.evidence.resolve()
root.mkdir(parents=True, exist_ok=False)
common = ["-unattended", "-NoSplash", "-NoSound", "-RenderOffscreen", "-windowed", "-ResX=1280", "-ResY=720"]
city = "/Game/Maps/SundaleGraybox?game=/Script/OddsWell.OddsWellLocomotionGameMode"
records = []


def launch(name, map_name, flags):
    log = root / (name + ".log")
    command = [str(exe), map_name, *common, *flags, "-UserDir=" + str(root / (name + "User")), "-abslog=" + str(log)]
    output = (root / (name + "-console.log")).open("w", encoding="utf-8")
    process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
    record = {"name": name, "pid": process.pid, "arguments": command}
    records.append(record)
    return process, record, output, log


def finish(run, markers):
    process, record, output, log = run
    try:
        record["exit"] = process.wait(timeout=120)
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
            record["terminated_after_timeout"] = True
        output.close()
        (root / "processes.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    text = log.read_text(encoding="utf-8", errors="replace")
    assert record["exit"] == 0, record
    assert all(marker in text for marker in markers), (record["name"], markers)
    record["required_markers"] = markers
    print(record["name"] + " PASS", flush=True)


for name, flags, markers in [
    ("locomotion", ["-LocomotionQa", "-LocomotionAutoExit", "-CharacterMotionCapture"], ["ODDSWELL_LOCOMOTION_QA|result=PASS", "ODDSWELL_CHARACTER_MOTION_QA|result=PASS"]),
    ("studio", ["-StudioQa", "-StudioAutoExit", "-StudioInteractionPromptPresentationQa", "-StudioPresentationQa"], ["ODDSWELL_STUDIO_QA|result=PASS", "ODDSWELL_STUDIO_INTERACTION_PROMPT_PRESENTATION_QA|result=PASS"]),
    ("camera", ["-CameraOrbitQa", "-CameraOrbitAutoExit"], ["ODDSWELL_CAMERA_ORBIT_QA|result=PASS"]),
]:
    finish(launch(name, city, flags), markers)

assert not subprocess.check_output(["powershell", "-NoProfile", "-Command",
    "$bindings = Get-NetUDPEndpoint -ErrorAction Stop; $bindings | Where-Object LocalPort -eq 17777 | Select-Object -ExpandProperty OwningProcess; exit 0"], text=True).strip(), "Gameplay port is already occupied"
server = launch("server", city + "?listen", ["-SharedCityQa", "-SharedCityAutoExit", "-SharedCityQaPreset=masculine_tone_1", "-multihome=127.0.0.1", "-port=17777"])
client = None
try:
    deadline = time.time() + 90
    while time.time() < deadline:
        text = server[3].read_text(encoding="utf-8", errors="replace") if server[3].exists() else ""
        if "listening on port 17777" in text:
            break
        assert server[0].poll() is None, "Server exited during startup"
        time.sleep(0.5)
    else:
        raise RuntimeError("Server startup timeout")
    binding = json.loads(subprocess.check_output(["powershell", "-NoProfile", "-Command",
        f"Get-NetUDPEndpoint -LocalPort 17777 -OwningProcess {server[0].pid} | Select-Object LocalAddress,LocalPort,OwningProcess | ConvertTo-Json -Compress"], text=True))
    assert binding["LocalAddress"] == "127.0.0.1"
    server[1]["gameplay_bind"] = binding
    client = launch("client", "127.0.0.1:17777", ["-SharedCityQa", "-SharedCityAutoExit", "-SharedCityQaPreset=feminine_tone_4"])
    finish(client, ["ODDSWELL_SHARED_SKELETAL_APPEARANCE|result=PASS"])
    finish(server, ["ODDSWELL_SHARED_CITY_PASS", "ODDSWELL_SHARED_SKELETAL_APPEARANCE|result=PASS", "ODDSWELL_SHARED_SKELETAL_MOTION|result=PASS"])
finally:
    for run in [server, client]:
        if run and run[0].poll() is None:
            run[0].terminate()
            run[0].wait(timeout=10)
            run[2].close()
(root / "processes.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
print("ODDSWELL_PACKAGED_CHARACTER_PASS")
