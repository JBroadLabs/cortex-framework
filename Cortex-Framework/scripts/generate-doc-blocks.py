#!/usr/bin/env python3
"""
Generate auto-populated blocks in AGENTS.md and PROTOCOL.md from state/agents_roster.yaml.
This script intentionally avoids external YAML dependencies and parses the expected schema
using a simple indentation-aware state machine tailored to the project's roster format.
"""
import os
import re
import sys
from typing import List, Dict, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROSTER_PATH = os.path.join(REPO_ROOT, "state", "agents_roster.yaml")
AGENTS_MD_PATH = os.path.join(REPO_ROOT, "AGENTS.md")
PROTOCOL_MD_PATH = os.path.join(REPO_ROOT, "PROTOCOL.md")

BEGIN_AGENTS = "<!-- BEGIN: GENERATED_AGENT_ROLES -->"
END_AGENTS = "<!-- END: GENERATED_AGENT_ROLES -->"
BEGIN_PROTOCOL = "<!-- BEGIN: GENERATED_PROTOCOL_ROLES -->"
END_PROTOCOL = "<!-- END: GENERATED_PROTOCOL_ROLES -->"


def parse_list_inline(value: str) -> List[str]:
    # Parse lists like ["a", "b", "c"] or [a, b]
    inner = value.strip()
    if inner.startswith("[") and inner.endswith("]"):
        inner = inner[1:-1]
    parts = [p.strip().strip('"').strip("'") for p in inner.split(",") if p.strip()]
    return parts


def parse_agents_roster(path: str) -> List[Dict[str, Any]]:
    agents: List[Dict[str, Any]] = []
    meta: Dict[str, Any] = {"roster_version": None, "schema_version": None}
    if not os.path.exists(path):
        raise FileNotFoundError(f"Roster file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current: Dict[str, Any] = None
    mode: str = None
    in_responsibilities = False
    resp_target: List[str] = None
    in_artifacts_in = False
    in_artifacts_out = False
    in_handoffs = False
    current_handoff: Dict[str, Any] = None
    in_mode_section = False
    mode_name = None

    for raw in lines:
        line = raw.rstrip("\n")
        # capture top-level versions
        m_rv = re.match(r"^\s*roster_version:\s*(.+)$", line)
        if m_rv:
            meta["roster_version"] = m_rv.group(1).strip()
            continue
        m_sv = re.match(r"^\s*schema_version:\s*(.+)$", line)
        if m_sv:
            meta["schema_version"] = m_sv.group(1).strip()
            continue
        # Start of an agent
        m_id = re.match(r"^\s*-\s*id:\s*(.+)$", line)
        if m_id:
            # flush previous
            if current:
                agents.append(current)
            current = {
                "id": m_id.group(1).strip(),
                "responsibilities": [],
                "artifacts_in": [],
                "artifacts_out": [],
                "protocol_roles": {"states": [], "handoffs": []},
                "modes": {},
            }
            # reset flags
            in_responsibilities = False
            in_artifacts_in = False
            in_artifacts_out = False
            in_handoffs = False
            current_handoff = None
            in_mode_section = False
            mode_name = None
            continue

        if current is None:
            continue

        # Top-level simple fields
        m_name = re.match(r"^\s*name:\s*(.+)$", line)
        if m_name:
            current["name"] = m_name.group(1).strip()
            continue
        m_summary = re.match(r"^\s*summary:\s*(.+)$", line)
        if m_summary:
            current["summary"] = m_summary.group(1).strip()
            continue
        m_persona = re.match(r"^\s*persona_file:\s*(.+)$", line)
        if m_persona:
            current["persona_file"] = m_persona.group(1).strip()
            continue

        # Responsibilities list (top-level)
        if re.match(r"^\s*responsibilities:\s*$", line):
            in_responsibilities = True
            resp_target = current["responsibilities"]
            continue
        if in_responsibilities:
            m_item = re.match(r"^\s*-\s*(.+)$", line)
            if m_item:
                resp_target.append(m_item.group(1).strip())
                continue
            # End of responsibilities when indentation changes or another key appears
            if line.strip() and not re.match(r"^\s*-\s*", line):
                in_responsibilities = False

        # Artifacts in/out lists
        if re.match(r"^\s*artifacts_in:\s*$", line):
            in_artifacts_in = True
            continue
        if in_artifacts_in:
            m_item = re.match(r"^\s*-\s*(.+)$", line)
            if m_item:
                current["artifacts_in"].append(m_item.group(1).strip())
                continue
            if line.strip() and not re.match(r"^\s*-\s*", line):
                in_artifacts_in = False

        if re.match(r"^\s*artifacts_out:\s*$", line):
            in_artifacts_out = True
            continue
        if in_artifacts_out:
            m_item = re.match(r"^\s*-\s*(.+)$", line)
            if m_item:
                current["artifacts_out"].append(m_item.group(1).strip())
                continue
            if line.strip() and not re.match(r"^\s*-\s*", line):
                in_artifacts_out = False

        # Protocol roles
        if re.match(r"^\s*protocol_roles:\s*$", line):
            mode = "protocol_roles"
            continue
        if mode == "protocol_roles":
            m_states = re.match(r"^\s*states:\s*(\[.*\])\s*$", line)
            if m_states:
                current["protocol_roles"]["states"] = parse_list_inline(m_states.group(1))
                continue
            if re.match(r"^\s*handoffs:\s*$", line):
                in_handoffs = True
                continue
            if in_handoffs:
                # start of handoff item
                m_hstart = re.match(r"^\s*-\s*from:\s*(.+)$", line)
                if m_hstart:
                    # flush previous handoff
                    if current_handoff:
                        current["protocol_roles"]["handoffs"].append(current_handoff)
                    current_handoff = {"from": m_hstart.group(1).strip()}
                    continue
                if current_handoff is not None:
                    m_to = re.match(r"^\s*to:\s*(.+)$", line)
                    if m_to:
                        current_handoff["to"] = m_to.group(1).strip()
                        continue
                    m_cond = re.match(r"^\s*conditions:\s*(\[.*\])\s*$", line)
                    if m_cond:
                        current_handoff["conditions"] = parse_list_inline(m_cond.group(1))
                        continue
                    # end of this handoff when a non-indented key appears
                    if line.strip() and not re.match(r"^\s*(from|to|conditions)\:", line) and not re.match(r"^\s*-\s*from:\s*", line):
                        if current_handoff:
                            current["protocol_roles"]["handoffs"].append(current_handoff)
                            current_handoff = None
                            in_handoffs = False

        # Modes
        if re.match(r"^\s*modes:\s*$", line):
            in_mode_section = True
            continue
        if in_mode_section:
            m_mode_name = re.match(r"^\s*(greenfield|brownfield)\:\s*$", line)
            if m_mode_name:
                mode_name = m_mode_name.group(1)
                current["modes"].setdefault(mode_name, {})
                resp_target = []
                continue
            if mode_name:
                if re.match(r"^\s*responsibilities:\s*$", line):
                    current["modes"][mode_name].setdefault("responsibilities", [])
                    resp_target = current["modes"][mode_name]["responsibilities"]
                    in_responsibilities = True
                    continue
                # end of mode section heuristics
                if re.match(r"^\s*\w+:", line) and not line.strip().startswith("responsibilities:"):
                    in_responsibilities = False

    # Flush last agent and last handoff
    if current_handoff and current:
        current["protocol_roles"]["handoffs"].append(current_handoff)
    if current:
        agents.append(current)

    # attach meta by returning as tuple-like dict
    return [{"_meta": meta}] + agents


def generate_agents_block(agents: List[Dict[str, Any]]) -> str:
    lines = []
    # meta header
    if agents and isinstance(agents[0], dict) and "_meta" in agents[0]:
        meta = agents[0]["_meta"]
        rv = meta.get("roster_version") or "unversioned"
        sv = meta.get("schema_version") or "unknown"
        lines.append(f"### Agents Roster (auto-generated)\n")
        lines.append(f"- Roster Version: {rv}\n")
        lines.append(f"- Schema Version: {sv}\n\n")
        agents_iter = agents[1:]
    else:
        lines.append("### Agents Roster (auto-generated)\n")
        agents_iter = agents
    for a in agents_iter:
        lines.append(f"- {a.get('name','Unnamed')} ({a.get('id')})\n")
        if a.get("summary"):
            lines.append(f"  - Summary: {a['summary']}\n")
        if a.get("persona_file"):
            lines.append(f"  - Persona: {a['persona_file']}\n")
        if a.get("responsibilities"):
            lines.append("  - Responsibilities:\n")
            for r in a["responsibilities"]:
                lines.append(f"    - {r}\n")
        if a.get("artifacts_in"):
            lines.append("  - Artifacts In: " + ", ".join(a["artifacts_in"]) + "\n")
        if a.get("artifacts_out"):
            lines.append("  - Artifacts Out: " + ", ".join(a["artifacts_out"]) + "\n")
        pr = a.get("protocol_roles", {})
        if pr.get("states"):
            lines.append("  - Protocol States: " + ", ".join(pr["states"]) + "\n")
        if pr.get("handoffs"):
            lines.append("  - Handoffs:\n")
            for h in pr["handoffs"]:
                cond = ", ".join(h.get("conditions", []))
                lines.append(f"    - {h.get('from')} -> {h.get('to')} | conditions: {cond}\n")
        modes = a.get("modes", {})
        # Only render Modes section if there are mode-specific responsibilities
        has_mode_resp = any(mconf.get("responsibilities") for mconf in modes.values()) if modes else False
        if has_mode_resp:
            lines.append("  - Modes:\n")
            for mname, mconf in modes.items():
                resp_list = mconf.get("responsibilities", [])
                if resp_list:
                    lines.append(f"    - {mname.capitalize()}:\n")
                    for r in resp_list:
                        lines.append(f"      - {r}\n")
        lines.append("\n")
    return "".join(lines)


def generate_protocol_block(agents: List[Dict[str, Any]]) -> str:
    lines = []
    # Extract meta if present
    meta = None
    agents_iter = agents
    if agents and isinstance(agents[0], dict) and "_meta" in agents[0]:
        meta = agents[0]["_meta"]
        agents_iter = agents[1:]

    lines.append("### Agent Protocol Roles (auto-generated)\n")
    if meta:
        rv = meta.get("roster_version") or "unversioned"
        sv = meta.get("schema_version") or "unknown"
        lines.append(f"- Roster Version: {rv}\n")
        lines.append(f"- Schema Version: {sv}\n\n")

    # Do NOT render any roster-derived summaries here to avoid duplication and context overload.
    # Keep PROTOCOL.md universal and reference the YAML as the single source of truth.
    lines.append(
        "Agent protocol roles (states and handoffs) are defined exclusively in state/agents_roster.yaml. "
        "This protocol document remains universal and intentionally does not duplicate roster content. "
        "Tools and agents MUST read directly from the YAML.\n"
    )
    lines.append("\n")
    return "".join(lines)


def replace_block(file_path: str, begin_marker: str, end_marker: str, new_block: str) -> None:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    begin_idx = content.find(begin_marker)
    end_idx = content.find(end_marker)
    if begin_idx == -1 or end_idx == -1:
        raise RuntimeError(f"Markers not found in {file_path}: {begin_marker} / {end_marker}")
    end_idx += len(end_marker)
    before = content[:begin_idx]
    after = content[end_idx:]
    replacement = f"{begin_marker}\n{new_block}{end_marker}"
    new_content = before + replacement + after
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    agents = parse_agents_roster(ROSTER_PATH)
    agents_block = generate_agents_block(agents)
    protocol_block = generate_protocol_block(agents)

    replace_block(AGENTS_MD_PATH, BEGIN_AGENTS, END_AGENTS, agents_block)
    replace_block(PROTOCOL_MD_PATH, BEGIN_PROTOCOL, END_PROTOCOL, protocol_block)
    print("Generated blocks updated in AGENTS.md and PROTOCOL.md from state/agents_roster.yaml")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)